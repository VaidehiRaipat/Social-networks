# Interactive POI visitation change maps\
\
This folder contains interactive web maps used to visualize how observed post-disaster visitation to third-place points of interest (POIs) differs from counterfactual-predicted visitation.\
\
## Files\
\
- `kepler_pois_polygons_R11.html`  \
  Interactive Kepler.gl map showing POI-level deviations between observed post-disaster visitation and counterfactual-predicted post-disaster visitation for the R11 co-location specification.\
\
## Study specification\
\
The R11 specification corresponds to:\
\
- spatial co-location threshold: 30 m\
- temporal overlap threshold: 5 min\
- pre-disaster period: October\'96November 2021\
- post-disaster period: January\'96February 2022\
- geography: Colorado study area\
- POI type: third-place POIs\
\
## Tooltip variables\
\
Each POI polygon includes the following variables:\
\
| Variable | Description |\
|---|---|\
| `poi` | Unique POI identifier |\
| `LOCATION_NAME` | Name of the POI |\
| `STREET_ADDRESS` | Street address of the POI |\
| `SUB_CATEGORY` | POI subcategory |\
| `pre_sum` | Total observed visits to the POI during the pre-disaster period |\
| `post_sum` | Total observed visits to the POI during the post-disaster period |\
| `log_pre_sum` | Log-transformed pre-disaster visitation count |\
| `z` | Standardized deviation of observed post-disaster visitation from counterfactual-predicted post-disaster visitation |\
| `z_log` | Log-adjusted standardized deviation of observed post-disaster visitation from counterfactual-predicted post-disaster visitation |\
\
## Interpretation\
\
The map layer is colored by `z_log`.\
\
The `z_log` value measures whether a POI received more or fewer observed post-disaster visits than expected under the counterfactual model.\
\
- Negative `z_log` values indicate that observed post-disaster visitation was lower than counterfactual-predicted visitation.\
- Positive `z_log` values indicate that observed post-disaster visitation was higher than counterfactual-predicted visitation.\
- Values near zero indicate that observed post-disaster visitation was close to the counterfactual prediction.\
\
The log adjustment accounts for baseline differences in POI visitation intensity, so deviations at low-traffic and high-traffic POIs are not interpreted as directly equivalent.\
\
For example, a POI with:\
\
- `post_sum = 0`\
- negative `z_log`\
\
received fewer observed post-disaster visits than expected under the counterfactual prediction.\
\
## How to view locally\
\
Open the HTML file directly in a web browser:\
\
```bash\
open kepler_pois_polygons_R11.html}
