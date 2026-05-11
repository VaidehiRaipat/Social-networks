# ============================================================
# Build Monthly POI-Weighted Co-location JSON
# Aggregates daily for_AM files into monthly dyad-level JSON
# ============================================================

import os
import json
import pandas as pd
from collections import defaultdict


def build_monthly_colocation(
    window_start,
    window_end,
    week_list,
    phase,
    prefix,
    revision,
    month_tag,
    stops_dir,
    min_active_days=2
):
    """
    Aggregates daily user-user POI co-location JSONs into
    a monthly dyad-level POI-weighted JSON.

    Parameters
    ----------
    window_start : str (YYYY-MM-DD)
    window_end   : str (YYYY-MM-DD)
    week_list    : list[str]
    phase        : str
    prefix       : str
    revision     : str
    month_tag    : str
    stops_dir    : str
    min_active_days : int
        Minimum days user must appear to be kept
    """

    # -------------------------------------------
    # Date range
    # -------------------------------------------
    date_range = pd.date_range(start=window_start, end=window_end)
    date_strings = [d.strftime("%Y%m%d") for d in date_range]

    # -------------------------------------------
    # Storage containers
    # -------------------------------------------
    edge_data = defaultdict(lambda: {
        "day_edge_count": 0,
        "pois": set(),
        "poi_day_counts": defaultdict(int),
    })

    user_day_count = defaultdict(set)
    num_days = 0
    valid_files = []

    # -------------------------------------------
    # Iterate through daily files
    # -------------------------------------------
    for week in week_list:
        for date in date_strings:

            json_path = os.path.join(
                stops_dir,
                phase,
                f"{week}/for_AM_{date}_{revision}.json"
            )

            if not os.path.exists(json_path):
                continue

            print(f"📖 Reading: {week} — {date}")
            valid_files.append((week, date))

            with open(json_path, "r") as f:
                try:
                    time_filtered_neighbors = json.load(f)
                except Exception as e:
                    print(f"⚠️ Error reading {json_path}: {e}")
                    continue

            # Convert keys to int for users
            time_filtered_neighbors = {
                int(u): {int(v): vv for v, vv in neigh.items()}
                for u, neigh in time_filtered_neighbors.items()
            }

            # ---------------------------------------
            # Track user activity
            # ---------------------------------------
            users_today = set(time_filtered_neighbors.keys())
            for neigh in time_filtered_neighbors.values():
                users_today.update(neigh.keys())

            for u in users_today:
                user_day_count[u].add(date)

            edge_count_today = 0

            # ---------------------------------------
            # Aggregate dyad data
            # ---------------------------------------
            for u, neigh_dict in time_filtered_neighbors.items():
                for v, poi_list in neigh_dict.items():

                    if not poi_list:
                        continue

                    key = tuple(sorted((u, v)))

                    # Count dyad-day presence
                    edge_data[key]["day_edge_count"] += 1

                    # Unique POIs per day
                    daily_pois = set(poi_list)

                    edge_data[key]["pois"].update(daily_pois)

                    for poi in daily_pois:
                        edge_data[key]["poi_day_counts"][poi] += 1

                    edge_count_today += 1

            print(f"✅ {len(users_today)} users and {edge_count_today} dyads for {date}")
            num_days += 1

    print(f"\n✅ Processed {num_days} total days")
    print(f"🔢 Total users tracked: {len(user_day_count)}")
    print(f"🔗 Total raw dyads accumulated: {len(edge_data)}")

    # -------------------------------------------
    # Active user filter
    # -------------------------------------------
    active_users = {
        u for u, days in user_day_count.items()
        if len(days) >= min_active_days
    }

    edge_data_filtered = {
        k: v for k, v in edge_data.items()
        if k[0] in active_users and k[1] in active_users
    }

    # -------------------------------------------
    # Build monthly JSON object
    # -------------------------------------------
    edge_data_monthly = {}

    for k, v in edge_data_filtered.items():

        day_edge_count = v["day_edge_count"]
        poi_day_counts = dict(v["poi_day_counts"])

        total_poi_day_hits = sum(poi_day_counts.values())

        poi_overlap_weight = (
            total_poi_day_hits / day_edge_count
            if day_edge_count > 0 else 0.0
        )

        edge_data_monthly[str(k)] = {
            "weight": day_edge_count,
            "pois": list(v["pois"]),
            "poi_counts": poi_day_counts,
            "poi_overlap_weight": poi_overlap_weight,
            "composite_weight": day_edge_count + poi_overlap_weight,
        }

    # -------------------------------------------
    # Save output
    # -------------------------------------------
    month_dir = os.path.join(
        stops_dir,
        f"{phase}/{prefix}_{month_tag}"
    )

    os.makedirs(month_dir, exist_ok=True)

    output_path = os.path.join(
        month_dir,
        f"{prefix}_{month_tag}_POI_weighted_colocation_{revision}.json"
    )

    with open(output_path, "w") as f:
        for k, v in edge_data_monthly.items():
            json.dump({k: v}, f)
            f.write("\n")

    print(f"\n✅ Saved monthly JSON: {output_path}")
    print(f"✅ Dyads after filtering: {len(edge_data_monthly)}")
    print(f"✅ Active users (≥{min_active_days} days): {len(active_users)}")
    print(f"🗂️  Valid daily files read: {len(valid_files)}")

    return output_path