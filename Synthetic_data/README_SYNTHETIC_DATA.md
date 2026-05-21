# Synthetic data package for the Social Networks R11 pipeline

This folder contains **fully synthetic** data that mimics the key schemas used by the GitHub notebooks. It is intended only for testing the code pipeline and demonstrating reproducibility. 

## Main synthetic inputs

- `Data/stop_df_perday_CO/Data/{phase}/{week}/stop_df_YYYYMMDD`  
  Synthetic daily stop tables with columns such as `cuebiq_id`, `lat`, `lng`, `stop_zoned_datetime`, `dwell_time_minutes`, `block_group_id`, and `classification_type`.

- `Data/stop_df_perday_CO/POIs/CO_pois_TP.csv`  
  Synthetic third-place POI table with `PLACEKEY`, POI category fields, lat/lng, and `polygon_geometry` WKT polygons.

- `Data/stop_df_perday_CO/home/{phase}/freq_home_*`  
  Synthetic user home-CBG files with `cuebiq_id`, `pre_disaster_home`, and `fips_code`.

Data/
└── stop_df_perday_CO/
    ├── daily_agg_to_weekly_Stops/
    │   ├── pre_disaster/
    │   │   └── week*/
    │   │       └── stop_df_YYYYMMDD
    │   └── post_disaster/
    │       └── week*/
    │           └── stop_df_YYYYMMDD
    ├── POIs/
    │   └── CO_pois_TP.csv
    ├── home/
    │   ├── pre_disaster/
    │   │   └── freq_home_*
    │   └── post_disaster/
    │       └── freq_home_*


## Proprietary data 

The real project uses proprietary Cuebiq/Spectus mobility data that cannot be redistributed. This synthetic package is a safe substitute for public GitHub testing and demonstration.

