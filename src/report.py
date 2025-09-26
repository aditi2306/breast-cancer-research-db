import json
import pandas as pd
from pathlib import Path
import numpy as np

def write_outputs(df_all, probs, y_test, results, output_dir: Path, feature_names, models):
    """Robust writer for pipeline outputs.
    - df_all: full dataframe (all rows ingested)
    - probs: numpy array or list of probabilities for the test split (length = n_test)
    - y_test: corresponding test labels
    - results: metrics dict
    - output_dir: Path where outputs will be saved
    - feature_names: list of feature names (for feature importance plot)
    - models: dict of trained models (optional, used for RF feature importances)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Write metrics.json
    (output_dir / 'metrics.json').write_text(json.dumps(results, indent=2))

    # 2) Create a robust predictions CSV:
    df_out = df_all.copy().reset_index(drop=True)

    # Create a column full of NaNs first
    prob_col_name = 'prob_demo'
    df_out[prob_col_name] = np.nan

    # If 'probs' is an array-like, convert to 1D numpy array
    try:
        probs_arr = np.asarray(probs).ravel()
    except Exception:
        probs_arr = np.array(list(probs))

    # Place probabilities into the top rows (safe fallback)
    n_probs = len(probs_arr)
    if n_probs <= len(df_out):
        df_out.loc[: n_probs - 1, prob_col_name] = probs_arr
    else:
        df_out.loc[:, prob_col_name] = probs_arr[: len(df_out)]

    # Write the predictions CSV
    df_out.to_csv(output_dir / 'patient_predictions.csv', index=False)

    # 3) Feature importance plot if RandomForest exists
    try:
        rf = models.get('rf', None)
        if rf is not None:
            import matplotlib.pyplot as plt
            import numpy as _np
            fi = rf.feature_importances_
            idx = _np.argsort(fi)[::-1]
            names = [feature_names[i] for i in idx]
            vals = fi[idx]
            plt.figure(figsize=(6,4))
            plt.bar(range(len(vals)), vals)
            plt.xticks(range(len(vals)), names, rotation=45, ha='right')
            plt.title('Feature Importance (Random Forest)')
            plt.tight_layout()
            plt.savefig(output_dir / 'feature_importance.png')
            plt.close()
    except Exception as e:
        # do not crash the whole pipeline on plotting issues
        print("Warning: could not write feature importance plot:", e)
