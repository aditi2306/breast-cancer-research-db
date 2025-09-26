# Breast Cancer Diagnosis Mini-Project (Governance + ML)

This demo shows a lightweight, interview-ready pipeline for a healthcare ML task:
- Ingest the Wisconsin Breast Cancer dataset (scikit-learn)
- Simulate clinical records and store in a SQLite DB
- Anonymise patient identifiers (hashing)
- Train baseline models (Logistic Regression, Random Forest)
- Evaluate with ROC-AUC and PR-AUC; output reports and plots
- (Optional) Streamlit UI for running the pipeline

## Setup (Windows / macOS / Linux)
```bash
cd breast_cancer_demo
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Run the pipeline
```bash
python -m src.main
```

Outputs will appear in `src/output/`:
- metrics.json
- roc_pr_curve.png
- feature_importance.png
- patient_predictions.csv

## Optional UI
```bash
streamlit run app.py
```

