import pandas as pd
import numpy as np

def extract_model_results(model, model_name, model_type=None, round_digits=3):
    """
    Returns tidy dataframe:
    Variable | Coefficient | P_value | CI_low | CI_high | R2 | Model | ModelType | significant
    Works for OLS and Logit (uses rsquared / prsquared if available).

    Parameters
    ----------
    model : fitted statsmodels result
    model_name : str
    model_type : str or None
        Optional manual label ("OLS", "Logit", etc.). If None, inferred.
    round_digits : int
        Number of decimals to round numeric outputs to.
    """
    coef = model.params
    pval = model.pvalues

    ci = model.conf_int()
    ci.columns = ["CI_low", "CI_high"]

    # R2 / pseudo-R2
    if hasattr(model, "rsquared"):
        r2 = float(model.rsquared)
        inferred_type = "OLS"
    elif hasattr(model, "prsquared"):
        r2 = float(model.prsquared)
        inferred_type = "Logit"
    else:
        r2 = np.nan
        inferred_type = "Other"

    if model_type is None:
        model_type = inferred_type

    out = pd.DataFrame({
        "Variable": coef.index.astype(str),
        "Coefficient": coef.values,
        "P_value": pval.reindex(coef.index).values,
        "CI_low": ci.loc[coef.index, "CI_low"].values,
        "CI_high": ci.loc[coef.index, "CI_high"].values,
    })

    out["R2"] = r2
    out["Model"] = model_name
    out["ModelType"] = model_type

    # significance flag (computed BEFORE rounding)
    out["significant"] = pd.to_numeric(out["P_value"], errors="coerce") < 0.05

    # ensure numeric
    num_cols = ["Coefficient", "P_value", "CI_low", "CI_high", "R2"]
    for c in num_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    # round numeric values to requested decimals (default = 3)
    out[num_cols] = out[num_cols].round(round_digits)

    return out