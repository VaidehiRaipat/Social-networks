# Social-networks
Disaster-induced behavioral change restructures social networks toward bonding ties.

# Social Networks: POI-weighted co-location and post-disaster social capital workflow

This repository contains a GitHub-ready version of the notebook workflow for constructing and analyzing POI-weighted social contact networks from anonymized mobility stops and third-place POI data - where a tie is created when two users are observed at the same POI within a 30 m spatial radius, on the same day, during the study activity window, with at least 5 minutes of temporal overlap. The workflow is organized for the paper: Disaster-induced behavioral change restructures social networks toward bonding ties. In this project we develop a spatially embedded, dynamic network framework that operationalizes social capital as a network of repeated encounter opportunities inferred from large-scale mobility data. We construct temporal co-presence networks at third places to track how socio-spatial networks reorganize under disruption. We apply this framework to communities affected by the 2021 Marshall Fire in Colorado. We find that disaster-induced displacement leads to substantial contraction of socio-spatial networks, with mean weighted degree decreasing by 48\%. To isolate underlying mechanisms, we develop two counterfactual models: a random removal model and a behaviour-informed model in which individuals are removed based on their estimated propensity to evacuate. Both counterfactuals predict substantially lower connectivity (37\% and 28\% lower mean weighted degree, respectively) than observed, indicating that post-disaster connectivity remains systematically higher than expected based on displacement behavior alone. Structural analysis of the network reveals that this residual connectivity is disproportionately concentrated among bonding ties between sociodemographically similar individuals, while bridging ties are comparatively fragile. 
Furthermore, interaction becomes increasingly located around third places, suggesting that these places act as spatial anchors for the persistence of social ties under disruption. 

## Repository status

This is a code-and-documentation repository. It does **not** include raw mobility data, proprietary provider data, individual-level records, large intermediate files, or generated outputs.

## Important data note

The mobility data used by this project are proprietary Cuebiq mobility data. These data are not public, are not redistributed here, and should not be committed to GitHub. Any user-level mobility records, home-location files, stop tables, POI-matched stop tables, dyad-level JSONs, graph PKLs, or generated outputs must remain outside the repository unless they are fully approved, non-sensitive, and shareable under the data-use agreement.

## Repository structure

```text
social-networks-github-ready/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── R8_1-CO_Weekly_adjacency_matrix.ipynb
│   ├── R8_2-CO_Randomremoval_interaction.ipynb
│   ├── R8_3-CO_Randomgraph.ipynb
│   ├── R8_4-CO_centralities_exploration.ipynb
│   ├── R8_5-CO_behaviorbased.ipynb
│   ├── R8_6-CO_behaviorbased_interaction.ipynb
│   ├── R8_7_CO_poilevel_changein_connections.ipynb
│   ├── R8_8_CO_POI_plot.ipynb
│   ├── R8_9_helper_CO_bonding_bridging_split.ipynb
│   ├── R8_9_CO_bonding_bridging_split-Copy1.ipynb
│   └── R8_10-CO_behaviorbased_interaction-splitgraphs.ipynb
├── scripts/
│   ├── R11_colocation_function.py
│   ├── R_monthly_poi_aggregation.py
│   ├── build_monthly_graphs_universal.py
│   ├── extract_model_results.py
│   └── plot_regression_models.py
└── docs/
|    ├── NOTEBOOK_INDEX.md
|    └── PATH_INVENTORY.md
└── Maps/
    ├── POI_Stats.html
    └── read_me_maps.tex
```

## Detailed workflow

| Step | Notebook | Main inputs | Main outputs | Feeds into |
|---:|---|---|---|---|
| 1 | `R8_1-CO_Weekly_adjacency_matrix.ipynb` | Cuebiq stops + home CBG + CO_pois_TP.csv + R11_colocation_function.py | Daily for_AM JSON → monthly POI-weighted JSON → R11 graph .pkl | R8_2, R8_3, R8_4, R8_9 |
| 2 | `R8_2-CO_Randomremoval_interaction.ipynb` | R11 graphs + dyad interactions + evacuation/home CBG data | Aligned dyads + random survivor/removal files | R8_3, R8_4 |
| 3 | `R8_3-CO_Randomgraph.ipynb` | Observed graphs + survivor files | Random survival counterfactual graph ensemble + metrics | R8_4, R8_7, R8_10 |
| 4 | `R8_4-CO_centralities_exploration.ipynb` | Observed and CF graph pickles | Node/network centrality summaries | R8_4 explaining, writing/figures |
| 5 | `R8_5-CO_behaviorbased.ipynb` | User features + evacuation labels + centralities + mobility variables | Behavior-informed yhat/probability tables | R8_6, R8_10 |
| 6 | `R8_6-CO_behaviorbased_interaction.ipynb` | Aligned dyads + yhat + home/Census files | Behavior-informed interaction/graph inputs | R8_10 |
| 7 | `R8_9_CO_bonding_bridging_split copy.ipynb` | User features + aligned dyads + graph pickles | Dyad similarity table + bonding/bridging graph files | R8_9.5, R8_10 |
| 8 | `R8_9.5_CO_bonding_bridging_split-Copy1.ipynb` | Dyad similarity + observed/CF graph pickles | Fixed-threshold bonding/bridging/refined/unclassified graph files | R8_10, figures |
| 9 | `R8_10-CO_behaviorbased_interaction-splitgraphs.ipynb` | Behavior-informed CFs + split-graph definitions | Split behavior-informed CF graph ensemble + metrics | Final comparison figures/tables |
| 10 | `R8_7_CO_poilevel_changein_connections.ipynb` | Observed/CF interactions + POIs + POI covariates + R_monthly_poi_aggregation.py | POI-level residual/change tables + regression outputs | R8_8, paper figures |
| 11 | `R8_8_CO_POI_plot.ipynb` | POI residuals + POI polygons + aligned dyads | POI maps and visualizations | Figures/supplement |

We provide an interactive supplementary map showing POI-level deviations between observed post-disaster visitation and counterfactual-predicted post-disaster visitation. The map is colored by $z_{\log}$, a log-adjusted standardized deviation, where negative values indicate lower-than-predicted observed post-disaster visitation and positive values indicate higher-than-predicted visitation. 

## Environment

Install core Python dependencies with:

```bash
pip install -r requirements.txt
```

The workflow uses Jupyter/Python packages including `pandas`, `geopandas`, `numpy`, `scipy`, `scikit-learn`, `networkx`, `matplotlib`, `seaborn`, `statsmodels`, `geopy`, `shapely`, and `keplergl`.

## License

Code in this repository is released under the MIT License.

Data are not included. Mobility data used in this project are proprietary Cuebiq/Spectus data and are subject to separate data-use agreements. Census, POI, and geographic boundary datasets may also be subject to their own source-specific licenses. Users must obtain all required data access permissions independently.
```

## Confidentiality and reproducibility

This repository is designed for reproducible code organization, not data sharing. No raw mobility records, user identifiers, proprietary data, or sensitive derived outputs are committed.


# Note on synthetic data and path configuration

The data included in this repository are fully synthetic and are provided only to demonstrate the structure of the workflow and allow users to test the code pipeline. The original mobility data used in the study were provided by Cuebiq/Spectus under a data-use agreement and are proprietary. These real mobility records cannot be redistributed through GitHub.

Because the uploaded data are synthetic and intentionally minimal, some notebook paths, date ranges, filenames, and phase labels may need to be edited before running the notebooks. In the original analysis, the notebooks were configured for the full Cuebiq/Spectus file tree, with multiple pre- and post-disaster months. The synthetic package includes only a small example subset, including synthetic stop files for two pre-disaster dates, two post-disaster dates, synthetic pre-disaster home-CBG files, and synthetic POI data.

If running the notebooks with the synthetic data, users should first check and update:

- base data directories;
- `phase` names such as `pre_disaster`, `post_disaster`, `PDM`, or `PtDM`;
- date lists and month/week mappings;
- filenames for `stop_df_YYYYMMDD` files;
- paths to home-CBG files;
- paths to generated outputs such as JSON files, graph pickles, and metric tables.

The synthetic data are not intended to reproduce the empirical results of the study. They are included only for code testing, demonstration, and reproducibility of the computational workflow.
