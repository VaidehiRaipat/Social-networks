import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_coef_ci(
    results_df,
    *,
    var_order=None,
    var_pretty=None,
    model_pretty=None,
    models_to_plot=None,
    match_on="raw",  # "raw" | "pretty" | "either"
    alpha_sig=0.05,
    grey_non_sig=True,
    nonsig_color="lightgrey",
    nonsig_alpha=0.35,
    sig_alpha=0.95,
    tick_fontsize=12,
    marker_size=70,
    ci_lw=1.6,
    figsize=(12, 7),
    drop_intercept=True,
    drop_category_dummies=False,
    category_prefixes=None,   # e.g. ["C(SUB_CATEGORY)[T.", "C(TOP_CATEGORY)[T."]
    legend=True,
    legend_loc="upper left",
    legend_bbox_to_anchor=(1.02, 1.0),
    legend_fontsize=12,
    show_r2_in_legend=True,
    xline_zero=True,
    x_label="Coefficient",
    title=None,
    model_colors=None,        # NEW: dict {"Model label": "#hex"}
    model_markers=None,       # NEW: dict {"Model label": "o"}
    return_ax=False,
):
    """
    Generic coefficient plot with CIs.

    Expected columns in results_df:
      - Variable
      - Coefficient
      - CI_low
      - CI_high
      - Model
      - P_value  (or 'significant')
      - R2       (optional if show_r2_in_legend=False)

    Notes:
      - Can plot OLS and Logit together, but coefficient magnitudes are not directly comparable.
      - Better to plot separately if magnitude interpretation matters.
    """
    required = {"Variable", "Coefficient", "CI_low", "CI_high", "Model"}
    missing = required - set(results_df.columns)
    if missing:
        raise ValueError(f"results_df is missing required columns: {sorted(missing)}")

    df = results_df.copy()

    var_pretty = {} if var_pretty is None else var_pretty
    model_pretty = {} if model_pretty is None else model_pretty
    category_prefixes = [] if category_prefixes is None else category_prefixes
    model_colors = {} if model_colors is None else model_colors
    model_markers = {} if model_markers is None else model_markers

    # Pretty labels
    df["Variable_pretty"] = df["Variable"].map(var_pretty).fillna(df["Variable"])
    df["Model_pretty"] = df["Model"].map(model_pretty).fillna(df["Model"])

    # Filter models
    if models_to_plot is not None:
        wanted = set(map(str, models_to_plot))
        if match_on == "raw":
            df = df[df["Model"].astype(str).isin(wanted)].copy()
        elif match_on == "pretty":
            df = df[df["Model_pretty"].astype(str).isin(wanted)].copy()
        elif match_on == "either":
            df = df[
                df["Model"].astype(str).isin(wanted) |
                df["Model_pretty"].astype(str).isin(wanted)
            ].copy()
        else:
            raise ValueError("match_on must be one of {'raw','pretty','either'}")

    if df.empty:
        raise ValueError("After filtering, no rows remain.")

    # Significance flag
    if "significant" not in df.columns:
        if "P_value" not in df.columns:
            raise ValueError("Need either 'significant' column or 'P_value'.")
        df["significant"] = pd.to_numeric(df["P_value"], errors="coerce") < float(alpha_sig)

    # Drop intercept
    if drop_intercept:
        df = df[~df["Variable"].astype(str).isin(["Intercept", "const"])].copy()

    # Drop category dummies if requested
    if drop_category_dummies:
        prefixes = ["C(SUB_CATEGORY)[T.", "C(TOP_CATEGORY)[T."] + list(category_prefixes)
        vstr = df["Variable"].astype(str)
        mask_keep = np.ones(len(df), dtype=bool)
        for p in prefixes:
            mask_keep &= ~vstr.str.startswith(p)
        df = df[mask_keep].copy()

    if df.empty:
        raise ValueError("No rows left after dropping intercept/dummies.")

    # Variable order
    if var_order is None:
        ordered_vars = df["Variable_pretty"].drop_duplicates().tolist()
    else:
        base = [var_pretty.get(v, v) for v in var_order]
        rest = [v for v in df["Variable_pretty"].drop_duplicates().tolist() if v not in base]
        ordered_vars = base + rest

    df["Variable_pretty"] = pd.Categorical(
        df["Variable_pretty"], categories=ordered_vars, ordered=True
    )
    df = df.sort_values(["Variable_pretty", "Model_pretty"]).copy()

    # Models
    models = df["Model_pretty"].drop_duplicates().tolist()
    if not models:
        raise ValueError("No models found to plot.")

    # Default colors and markers (only if not provided)
    default_colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["#1f77b4"])
    base_color_map = {}
    for i, m in enumerate(models):
        base_color_map[m] = model_colors.get(m, default_colors[i % len(default_colors)])

    default_markers = ["o", "s", "D", "^", "v", "P", "X", "*", "<", ">", "h", "H"]
    marker_map = {}
    for i, m in enumerate(models):
        marker_map[m] = model_markers.get(m, default_markers[i % len(default_markers)])

    # Legend labels
    if show_r2_in_legend and "R2" in df.columns:
        r2_by_model = df.groupby("Model_pretty")["R2"].max()
        legend_label = {m: f"{m} (R²={r2_by_model.loc[m]:.3f})" for m in models}
    else:
        legend_label = {m: m for m in models}

    # Plot
    fig, ax = plt.subplots(figsize=figsize)

    all_categories = df["Variable_pretty"].cat.categories.tolist()
    y_pos = {v: i for i, v in enumerate(all_categories)}
    df["_y"] = df["Variable_pretty"].map(y_pos).astype(float)

    offsets = np.linspace(-0.20, 0.20, num=max(2, len(models)))
    model_offset = {m: offsets[i] for i, m in enumerate(models)}
    df["_y_dodge"] = df["_y"] + df["Model_pretty"].map(model_offset)

    handles, labels = [], []

    for m in models:
        sub = df[df["Model_pretty"] == m].copy()
        if sub.empty:
            continue

        sub_sig = sub[sub["significant"]].copy()
        sub_nsig = sub[~sub["significant"]].copy()

        # CI lines
        if len(sub_sig):
            ax.hlines(
                y=sub_sig["_y_dodge"],
                xmin=sub_sig["CI_low"],
                xmax=sub_sig["CI_high"],
                linewidth=ci_lw,
                color="grey",
                linestyle=":",
                alpha=0.85,
                zorder=1,
            )

        if len(sub_nsig):
            ax.hlines(
                y=sub_nsig["_y_dodge"],
                xmin=sub_nsig["CI_low"],
                xmax=sub_nsig["CI_high"],
                linewidth=ci_lw,
                color=(nonsig_color if grey_non_sig else "grey"),
                linestyle=":",
                alpha=(nonsig_alpha if grey_non_sig else 0.85),
                zorder=1,
            )

        # Non-significant points
        if len(sub_nsig):
            ax.scatter(
                sub_nsig["Coefficient"],
                sub_nsig["_y_dodge"],
                s=marker_size,
                marker=marker_map[m],
                color=(nonsig_color if grey_non_sig else base_color_map[m]),
                alpha=(nonsig_alpha if grey_non_sig else sig_alpha),
                edgecolor="none",
                zorder=2,
            )

        # Significant points
        if len(sub_sig):
            sc = ax.scatter(
                sub_sig["Coefficient"],
                sub_sig["_y_dodge"],
                s=marker_size,
                marker=marker_map[m],
                color=base_color_map[m],
                alpha=sig_alpha,
                edgecolor="none",
                zorder=3,
            )
        else:
            sc = ax.scatter([], [], s=marker_size, marker=marker_map[m], color=base_color_map[m])

        handles.append(sc)
        labels.append(legend_label[m])

    if xline_zero:
        ax.axvline(0, color="black", linestyle="--", linewidth=1, zorder=0)

    ax.set_yticks(range(len(all_categories)))
    ax.set_yticklabels(all_categories)
    ax.tick_params(axis="x", labelsize=tick_fontsize)
    ax.tick_params(axis="y", labelsize=tick_fontsize)

    ax.set_xlabel(x_label, fontsize=tick_fontsize + 1)
    ax.set_ylabel("")
    if title is not None:
        ax.set_title(title, fontsize=tick_fontsize + 2)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    if legend:
        ax.legend(
            handles,
            labels,
            loc=legend_loc,
            bbox_to_anchor=legend_bbox_to_anchor,
            frameon=False,
            fontsize=legend_fontsize,
            title_fontsize=legend_fontsize,
        )

    plt.tight_layout()

    if return_ax:
        return fig, ax
    plt.show()