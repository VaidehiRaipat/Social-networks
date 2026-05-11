# ============================================================
# UNIVERSAL Monthly Graph Builder
# Works for any revision / phase / prefix
# No hard-coded months
# ============================================================

import os
import json
import ast
import pickle
import re
import networkx as nx


def build_monthly_graphs(
    stops_dir,
    graph_dir,
    revision=None,
    save_graphs=True,
    recursive=True,
):
    """
    Automatically finds all monthly POI-weighted JSON files
    and builds one NetworkX graph per file.

    Compatible with any:
        - revision (R6, R7, R8, R8.1, R9, ...)
        - phase (pre_disaster, post_disaster, etc.)
        - prefix (PDM, PtDM, etc.)
        - month

    Parameters
    ----------
    stops_dir : str
        Root stops directory.
    graph_dir : str
        Output directory for graphs.
    revision : str or None
        If provided, filters files by revision.
        If None → builds for all revisions found.
    save_graphs : bool
        Whether to save .pkl files.
    recursive : bool
        Search recursively inside stops_dir.

    Returns
    -------
    dict
        {filename : NetworkX Graph}
    """

    graphs = {}

    # --------------------------------------------------------
    # 1️⃣ Discover JSON files
    # --------------------------------------------------------
    print("\n🔎 Searching for monthly POI-weighted JSON files...")

    json_files = []

    if recursive:
        for root, _, files in os.walk(stops_dir):
            for f in files:
                if "POI_weighted_colocation" in f and f.endswith(".json"):
                    if revision is None or revision in f:
                        json_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(stops_dir):
            if "POI_weighted_colocation" in f and f.endswith(".json"):
                if revision is None or revision in f:
                    json_files.append(os.path.join(stops_dir, f))

    if not json_files:
        print("❌ No matching JSON files found.")
        return {}

    print(f"✅ Found {len(json_files)} monthly files.")

    # --------------------------------------------------------
    # 2️⃣ Build Graph Per File
    # --------------------------------------------------------
    for monthly_json_path in sorted(json_files):

        filename = os.path.basename(monthly_json_path)

        print(f"\n🕸️ Building graph from {filename}")

        # ----------------------------------------------------
        # Extract metadata dynamically from filename
        # Example:
        # PDM_Oct2021_POI_weighted_colocation_R8.1.json
        # ----------------------------------------------------
        match = re.match(
            r"(?P<prefix>.+?)_(?P<month>.+?)_POI_weighted_colocation_(?P<rev>.+?)\.json",
            filename
        )

        if match:
            prefix = match.group("prefix")
            month = match.group("month")
            file_revision = match.group("rev")
        else:
            print("⚠️ Could not parse filename — using fallback metadata")
            prefix = "unknown"
            month = filename
            file_revision = revision

        # Infer phase from directory structure
        if "pre_disaster" in monthly_json_path:
            phase = "pre"
        elif "post_disaster" in monthly_json_path:
            phase = "post"
        else:
            phase = "unknown"

        G = nx.Graph()
        edge_counter = 0

        # ----------------------------------------------------
        # Load JSON
        # ----------------------------------------------------
        with open(monthly_json_path, "r") as f:
            for line in f:
                entry = json.loads(line)

                for key, value in entry.items():

                    u, v = ast.literal_eval(key)

                    if u == v:
                        continue

                    G.add_edge(
                        u, v,
                        weight=value.get("weight", 1),
                        poi_counts=value.get("poi_counts", {}),
                        num_pois=len(value.get("pois", [])),
                        poi_overlap_weight=value.get("poi_overlap_weight", 0),
                        composite_weight=value.get("composite_weight", 0)
                    )

                    edge_counter += 1

        # ----------------------------------------------------
        # Attach metadata
        # ----------------------------------------------------
        G.graph["month"] = month
        G.graph["phase"] = phase
        G.graph["prefix"] = prefix
        G.graph["revision"] = file_revision
        G.graph["source_file"] = filename

        graphs[filename] = G

        print(f"   Nodes: {G.number_of_nodes()}")
        print(f"   Edges: {G.number_of_edges()}")
        print(f"   Self-loops: {nx.number_of_selfloops(G)}")

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------
        if save_graphs:
            os.makedirs(graph_dir, exist_ok=True)

            output_path = os.path.join(
                graph_dir,
                f"{prefix}_{month}_graph_POI_weighted_{file_revision}.pkl"
            )

            with open(output_path, "wb") as gf:
                pickle.dump(G, gf)

            print(f"💾 Saved → {output_path}")

    return graphs