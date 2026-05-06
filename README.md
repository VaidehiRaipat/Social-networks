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
│   ├── R11_CO_Weekly_adjacency_matrix_function_workflow.ipynb
│   ├── R8_1-CO_Weekly_adjacency_matrix.ipynb
│   ├── R8_1-FL_Weekly_adjacency_matrix.ipynb
│   ├── R8_2-CO_Randomremoval_interaction.ipynb
│   ├── R8_3-CO_Randomgraph.ipynb
│   ├── R8_4-CO_centralities_exploration.ipynb
│   ├── R8_4-CO_explaining_centralities.ipynb
│   ├── R8_5-CO_behaviorbased.ipynb
│   ├── R8_6-CO_behaviorbased_interaction.ipynb
│   ├── R8_7_CO_poilevel_changein_connections.ipynb
│   ├── R8_8_CO_POI_plot.ipynb
│   ├── R8_9_CO_bonding_bridging_split copy.ipynb
│   ├── R8_9.5_CO_bonding_bridging_split-Copy1.ipynb
│   └── R8_10-CO_behaviorbased_interaction-splitgraphs.ipynb
├── scripts/
│   ├── R11_colocation_function.py
│   ├── R_monthly_poi_aggregation.py
│   ├── build_monthly_graphs_universal.py
│   ├── extract_model_results.py
│   └── plot_regression_models.py
└── docs/
    ├── NOTEBOOK_INDEX.md
    └── PATH_INVENTORY.md
```

## Detailed workflow: inputs, notebooks, outputs, and downstream use

| Step | Notebook / script | Main inputs | Main outputs | Used by next |
|---:|---|---|---|---|
| 0 | `scripts/R11_colocation_function.py` | Daily stop tables, POI polygons, home-location tables, R11 parameters | Daily user-user POI co-location adjacency JSONs: `for_AM_{date}_R11.json` | Step 1 monthly aggregation |
| 1 | `notebooks/R8_1-CO_Weekly_adjacency_matrix.ipynb` | Cuebiq stop files under `daily_agg_to_weekly_Stops/`, cleaned third-place POIs, home CBG files, `HOME_FILE_MAP`, `WEEK_DATE_MAP` | Daily adjacency JSONs for Oct 2021, Nov 2021, Jan 2022, Feb 2022 | Monthly dyad aggregation |
| 2 | `scripts/R_monthly_poi_aggregation.py` called from the R11 notebook | Daily `for_AM_{date}_R11.json` files | Monthly POI-weighted dyad JSONs: `PDM_Oct2021_POI_weighted_colocation_R11.json`, `PDM_Nov2021_...`, `PtDM_Jan2022_...`, `PtDM_Feb2022_...` | Graph construction |
| 3 | `scripts/build_monthly_graphs_universal.py` called from the R11 notebook | Monthly POI-weighted dyad JSONs | NetworkX graph PKLs: `PDM_Oct2021_graph_POI_weighted_R11.pkl`, `PDM_Nov2021_...`, `PtDM_Jan2022_...`, `PtDM_Feb2022_...` | Observed network metrics, random nulls, behavior-informed nulls, split graphs |
| 4 | `R8_2-CO_Randomremoval_interaction.ipynb` | Observed pre/post R11 graphs, user/home CBG information, survivor/removal counts | Random survival/removal counterfactual graph objects and interaction metrics | Random graph summaries and comparisons |
| 5 | `R8_3-CO_Randomgraph.ipynb` | Observed graphs and random-removal outputs | Random graph summaries, network-level metrics, node-level metrics | Centrality exploration and null comparisons |
| 6 | `R8_4-CO_centralities_exploration.ipynb` | Observed and counterfactual graph PKLs / metric CSVs | Centrality diagnostic tables and plots | Interpretation and model covariates |
| 7 | `R8_4-CO_explaining_centralities.ipynb` | Node/network centrality outputs | Centrality interpretation outputs and explanatory comparisons | Reporting and later model interpretation |
| 8 | `R8_5-CO_behaviorbased.ipynb` | User-level feature table, pre-disaster centralities, mobility features, socio-demographic attributes, observed survival/removal labels | Behavior-informed survival/removal predictions and model summaries | Behavior-informed counterfactual graph construction |
| 9 | `R8_6-CO_behaviorbased_interaction.ipynb` | Observed R11 graphs, behavior-informed probabilities, CBG-level survivor/removal constraints | Behavior-informed counterfactual interaction networks and graph metrics | Observed vs random vs behavior-informed comparison |
| 10 | `R8_7_CO_poilevel_changein_connections.ipynb` | Observed and counterfactual graphs, POI metadata, POI-user edge statistics | POI-level change tables, residual interaction summaries, place-level outputs | POI plots and substantive interpretation |
| 11 | `R8_8_CO_POI_plot.ipynb` | POI-level change outputs, POI metadata, geographic layers | POI maps and POI-level figures | Manuscript / presentation figures |
| 12 | `R8_9_CO_bonding_bridging_split copy.ipynb` | R11 observed/counterfactual graphs, dyad homophily/similarity table, structural metrics | Bonding, bridging-refined, and unclassified graph files | Split-graph comparison |
| 13 | `R8_9.5_CO_bonding_bridging_split-Copy1.ipynb` | Outputs from the bonding/bridging split workflow | Refined split-graph thresholding outputs | Robustness / final split graph workflow |
| 14 | `R8_10-CO_behaviorbased_interaction-splitgraphs.ipynb` | Bonding, bridging-refined, and unclassified graphs; behavior-informed counterfactual outputs | Tie-type-specific observed/random/behavior-informed network metrics and plots | Manuscript results |```

## Environment

Install core Python dependencies with:

```bash
pip install -r requirements.txt
```

The workflow uses Jupyter/Python packages including `pandas`, `geopandas`, `numpy`, `scipy`, `scikit-learn`, `networkx`, `matplotlib`, `seaborn`, `statsmodels`, `geopy`, `shapely`, and `keplergl`.

## Suggested execution order

```text
1. notebooks/R11_CO_Weekly_adjacency_matrix_function_workflow.ipynb
2. notebooks/R8_2-CO_Randomremoval_interaction.ipynb
3. notebooks/R8_3-CO_Randomgraph.ipynb
4. notebooks/R8_4-CO_centralities_exploration.ipynb
5. notebooks/R8_4-CO_explaining_centralities.ipynb
6. notebooks/R8_5-CO_behaviorbased.ipynb
7. notebooks/R8_6-CO_behaviorbased_interaction.ipynb
8. notebooks/R8_7_CO_poilevel_changein_connections.ipynb
9. notebooks/R8_8_CO_POI_plot.ipynb
10. notebooks/R8_9_CO_bonding_bridging_split copy.ipynb
11. notebooks/R8_9.5_CO_bonding_bridging_split-Copy1.ipynb
12. notebooks/R8_10-CO_behaviorbased_interaction-splitgraphs.ipynb

## License

Code in this repository is released under the MIT License.

Data are not included. Mobility data used in this project are proprietary Cuebiq/Spectus data and are subject to separate data-use agreements. Census, POI, and geographic boundary datasets may also be subject to their own source-specific licenses. Users must obtain all required data access permissions independently.
```

## Confidentiality and reproducibility

This repository is designed for reproducible code organization, not data sharing. No raw mobility records, user identifiers, proprietary data, or sensitive derived outputs are committed.
