# Interactive POI Visitation Deviation Map

This folder contains an interactive web map used to visualize how observed post-disaster visitation to third-place points of interest (POIs) differs from counterfactual-predicted post-disaster visitation.

The map is provided as a standalone HTML file generated using Kepler.gl. It can be downloaded and opened locally in a web browser.

## File

- `POI_Stats.html`  
  Interactive Kepler.gl map showing POI-level deviations between observed post-disaster visitation and counterfactual-predicted post-disaster visitation.

## Study specification

The map corresponds to the R11 co-location specification:

- spatial co-location threshold: 30 m
- temporal overlap threshold: 5 min
- pre-disaster period: October–November 2021
- post-disaster period: January–February 2022
- geography: Colorado study area
- POI type: third-place POIs

## Tooltip variables

Each POI polygon includes the following variables:

| Variable | Description |
|---|---|
| `poi` | Unique POI identifier |
| `LOCATION_NAME` | Name of the POI |
| `STREET_ADDRESS` | Street address of the POI |
| `SUB_CATEGORY` | POI subcategory |
| `pre_sum` | Total observed visits to the POI during the pre-disaster period |
| `post_sum` | Total observed visits to the POI during the post-disaster period |
| `log_pre_sum` | Log-transformed pre-disaster visitation count |
| `z` | Standardized deviation of observed post-disaster visitation from counterfactual-predicted post-disaster visitation |
| `z_log` | Log-adjusted standardized deviation of observed post-disaster visitation from counterfactual-predicted post-disaster visitation |

## Interpretation

The active map layer is colored by `z_log`.

The `z_log` value measures whether a POI received more or fewer observed post-disaster visits than expected under the counterfactual model.

- Negative `z_log` values indicate that observed post-disaster visitation was lower than counterfactual-predicted visitation.
- Positive `z_log` values indicate that observed post-disaster visitation was higher than counterfactual-predicted visitation.
- Values near zero indicate that observed post-disaster visitation was close to the counterfactual prediction.

The log adjustment accounts for baseline differences in POI visitation intensity. This helps avoid treating deviations at low-traffic and high-traffic POIs as directly equivalent.

For example, a POI with `post_sum = 0` and a negative `z_log` received fewer observed post-disaster visits than expected under the counterfactual prediction.

## How to view the map

To view the interactive map locally:

1. Download the HTML file from this folder.
2. Open `POI_Stats.html` in a web browser such as Chrome, Firefox, Safari, or Edge.

The file should open as an interactive Kepler.gl map. No Python, Jupyter Notebook, or GIS software is required.
