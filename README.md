# Breast Cancer Diagnosis Mini-Project (Governance + ML)

This demo shows a lightweight, interview-ready pipeline for a healthcare ML task:
- Ingest the Wisconsin Breast Cancer dataset (scikit-learn)
- Simulate clinical records and store in a SQLite DB
- Anonymise patient identifiers (hashing)
- Train baseline models (Logistic Regression)
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
<img width="1500" height="747" alt="image" src="https://github.com/user-attachments/assets/d00830b1-65af-48c3-824b-7c9125cfb15e" />
<img width="1434" height="1137" alt="image" src="https://github.com/user-attachments/assets/7e037003-8f73-4445-8758-7bc0c6cf72f7" />


