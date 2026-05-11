#def R10 - spatial join for poi and stop matching, closest centrid to make sure each stop is match to only one poi, users to be 30 m apar and visit a poi at the same day to be connected no temporal overlap (evening weekday and weekend), makes sure each stop has only one poi matched to it, also makes sure that all stops across all dates are included - this part was same as R8.1, only temporal overlap added of 5 minutes 

# A tie is created between two users if:
# 	1.	✔ Both stops fall inside a POI polygon
# 	2.	✔ Stops are within 30 meters (BallTree haversine)
# 	3.	✔ Stops share the same POI (PLACEKEY)
# 	4.	✔ Stops occur on the same calendar day
# 	5.	✔ Stops occur during:
# 	•	Weekday evenings (17–23) OR
# 	•	Weekend (all hours)
# 	6.	✔ Temporal overlap ≥ 5 minutes
# 	7.	✔ Home stops removed
# 	8.	✔ Recurring/work stops removed
# 	9.	✔ Timezone normalized to Denver

#This buils a jason as explained below:
# For a given output_date (e.g., "20220203"), week folder, and phase, it creates a daily user–user co-location adjacency JSON
# Json Structure
# 
#   "userA": {
#     "userB": ["PLACEKEY_1", "PLACEKEY_2"],
#     "userC": ["PLACEKEY_9"]
#   },
#   "userB": {
#     "userA": ["PLACEKEY_1"]
#   }
# }

import os
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import wkt
from sklearn.neighbors import BallTree
import json
from collections import defaultdict
import sys
import csv

# Set this at the module level
csv.field_size_limit(sys.maxsize)

STATE_TZ_MAP = {
    "CO": "America/Denver",
    "FL": "America/New_York",
    "TX": "America/Chicago",
    "CA": "America/Los_Angeles"
}

def run_daily_colocation(
    output_date,
    Week,
    Phase,
    revision,
    stops_dir,
    pois_dir,
    base,
    HOME_FILE_MAP,
    state,
    bbox=None,
    timezone=None,
    R_meters=30
):
    """
    Builds a daily user-user co-location adjacency:
      - stop must be inside a POI polygon (PLACEKEY)
      - candidate pairs must be within R_meters spatially
      - pair must share the same POI (same PLACEKEY / matched_pois overlap)
      - keep only weekday evenings (17–23) or weekends
      - keep same-day filter (implemented correctly at STOP level, not user level)
    Writes: for_AM_{output_date}_{revision}.json
    """
    try:
        # daily stop table 
        # Load stops
        # Expected columns include at least:cuebiq_id, lat, lng, stop_zoned_datetime, dwell_time_minutes, block_group_id
        # CORRECTED PATH JOINING AND LOADING
        stop_file_path = os.path.join(stops_dir, Phase, Week, f"stop_df_{output_date}")
        
        # The engine='python' goes here, inside read_csv
        df_raw_stops = pd.read_csv(stop_file_path, engine="python", on_bad_lines='skip')

        # Loads POIs with polygon boundaries (WKT strings) - Converts them to Shapely geometries
        # Load POIs (already cleaned + clustered)
        # Makes a GeoDataFrame of POI's to support spatial join
        poi_file_path = os.path.join(pois_dir, f"{state}_pois_TP.csv")
        pois = pd.read_csv(poi_file_path, engine="python")
        pois["polygon_geometry"] = pois["polygon_geometry"].apply(
            lambda x: wkt.loads(x) if isinstance(x, str) else x
        )
        gdf_pois_poly = gpd.GeoDataFrame(pois, geometry="polygon_geometry", crs="EPSG:4326")

        # Uses a lookup HOME_FILE_MAP[(Phase, Week)] to pick the right home file
        # Load homes (phase + week specific)
        # Merges into stops so each stop knows the user’s home CBG
        home_file = HOME_FILE_MAP.get((Phase, Week))
        if home_file is None:
            raise FileNotFoundError(f"No home file defined for Phase={Phase}, Week={Week}")

        home_path = os.path.join(base, "home", Phase, home_file)
        home_df = pd.read_csv(home_path)[["cuebiq_id", "pre_disaster_home"]]

        home_df["cuebiq_id"] = home_df["cuebiq_id"].astype(str)
        df_raw_stops["cuebiq_id"] = df_raw_stops["cuebiq_id"].astype(str)

        df = df_raw_stops.merge(home_df, on="cuebiq_id", how="left")

        # Removes stops that occur in the same CBG as the user’s home
        # Drop home stops
        # focus on “out-of-home” activity
        df["block_group_id"] = df["block_group_id"].astype(str)
        df["pre_disaster_home"] = df["pre_disaster_home"].astype(str)

        df = df[df["block_group_id"] != df["pre_disaster_home"]].copy()
        df = df[df['classification_type'] != "RECURRING_AREA"].copy() # remove work location acptured as users reccuring location
        
        # Converts timestamp strings to datetime
        # Time handling 
        # Ensures the times are in colorado time
        # Computes end time from dwell time
        
        df["stop_zoned_datetime"] = pd.to_datetime(
            df["stop_zoned_datetime"],
            errors="coerce",
            utc=True
        )

        # Drop invalid timestamps
        df = df.dropna(subset=["stop_zoned_datetime"])

        # Convert to local Colorado time
        # If no timezone is passed, look it up via state. Default to UTC if not found.
        target_tz = timezone or STATE_TZ_MAP.get(state, "UTC")
        df["stop_local"] = df["stop_zoned_datetime"].dt.tz_convert(target_tz)

        # Ensure dwell is numeric
        df["dwell_time_minutes"] = pd.to_numeric(
            df["dwell_time_minutes"],
            errors="coerce"
        )

        df = df.dropna(subset=["dwell_time_minutes"])

        df["end_local"] = df["stop_local"] + pd.to_timedelta(
            df["dwell_time_minutes"],
            unit="m"
        )

        # Crops stops to a hard-coded lat/lon rectangle around Boulder
        # Boulder bounding box
        # This speeds up spatial joins and neighbor search and focuses analysis area
        if bbox is not None:
            lat_min, lat_max, lng_min, lng_max = bbox
            df = df[
                (df["lat"] > lat_min) & (df["lat"] < lat_max) &
                (df["lng"] > lng_min) & (df["lng"] < lng_max)
            ].copy()

        gdf_stops = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["lng"], df["lat"]),
            crs="EPSG:4326"
        )

        # Creates point geometries from stop lat/lng
        # Spatial join (polygon POIs) - assigns each stop a POI polygon if the stop point lies within / intersects a polygon
        # Keeps only stops matched to a POI
        gdf_stops = gdf_stops.drop(
            columns=[c for c in ["index_left", "index_right"] if c in gdf_stops.columns],
            errors="ignore",
        )
        gdf_pois_poly = gdf_pois_poly.drop(
            columns=[c for c in ["index_left", "index_right"] if c in gdf_pois_poly.columns],
            errors="ignore",
        )

        df_poi = gpd.sjoin(gdf_stops, gdf_pois_poly, how="left", predicate="intersects")
        df_poi = df_poi[~df_poi["PLACEKEY"].isna()].copy()

        # Make POI list per row (keeps your existing logic: single PLACEKEY per join-row) - Creates a list column of matched POIs per stop row
        df_poi["matched_pois"] = df_poi["PLACEKEY"].apply(lambda x: [x])

        # use stop_local instead of stop_zoned date time to ensure local time stop
        # Temporal filters (weekday evening + weekend)
        # ----------------------------
        df_poi["hour"] = df_poi["stop_local"].dt.hour
        df_poi["weekday"] = df_poi["stop_local"].dt.weekday
        df_poi["stop_date"] = df_poi["stop_local"].dt.date

        is_weekday_evening = df_poi["weekday"].between(0, 4) & df_poi["hour"].between(17, 23)
        is_weekend = df_poi["weekday"].isin([5, 6])
        df_poi = df_poi[is_weekday_evening | is_weekend].copy()

        # If nothing left, still write an empty file (optional) or just return True
        # Here: write empty adjacency to keep downstream consistent
        if df_poi.shape[0] == 0:
            out_path = os.path.join(stops_dir, f"{Phase}/{Week}/for_AM_{output_date}_{revision}.json")
            with open(out_path, "w") as f:
                json.dump({}, f)
            return True
        


        # BallTree finds all stop points within radius R_meters
        # Haversine uses radians and Earth radius ≈ 6,371,000m
        # neighbors[i] = indices of stop records close to stop i.
        coords = np.deg2rad(df_poi[["lat", "lng"]].values)
        tree = BallTree(coords, metric="haversine")
        neighbors = tree.query_radius(coords, r=R_meters / 6371000)

        cuebiq_ids = df_poi["cuebiq_id"].values
        matched_pois = df_poi["matched_pois"].values
        stop_dates = df_poi["stop_date"].values  # aligned with rows


        # THIS POINT ONWARDS THE FUNCTION IS DIFFERENT FROM R8.1, upto save
        # Build co-location edges with ≥5 min temporal overlap
        # ----------------------------

        co_location = defaultdict(lambda: defaultdict(set))

        start_times = df_poi["stop_local"].values
        end_times   = df_poi["end_local"].values

        for i in range(len(df_poi)):

            u = cuebiq_ids[i]
            u_date = stop_dates[i]
            pois_i = set(matched_pois[i])

            u_start = start_times[i]
            u_end   = end_times[i]

            for j in neighbors[i]:

                if i == j:
                    continue

                v = cuebiq_ids[j]
                if u == v:
                    continue

                if stop_dates[j] != u_date:
                    continue

                shared = pois_i.intersection(matched_pois[j])
                if not shared:
                    continue

                v_start = start_times[j]
                v_end   = end_times[j]

                overlap = min(u_end, v_end) - max(u_start, v_start)

                if overlap > np.timedelta64(0, 'ns'):
                    if overlap / np.timedelta64(1, 'm') >= 5:
                        co_location[u][v].update(shared)
                        co_location[v][u].update(shared)

        # ----------------------------
        # Save JSON
        # ----------------------------
        out_path = os.path.join(stops_dir, f"{Phase}/{Week}/for_AM_{output_date}_{revision}.json")
        with open(out_path, "w") as f:
            json.dump(
                {u: {v: list(p) for v, p in neigh.items()} for u, neigh in co_location.items()},
                f
            )

        return True

    except Exception as e:
        print(f"❌ Failed {Phase} | {Week} | {output_date}: {e}")
        return False


