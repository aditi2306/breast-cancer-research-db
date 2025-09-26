# app.py
import os, sys, io, json
from pathlib import Path
import pandas as pd
import streamlit as st
from datetime import datetime,timezone
from sqlalchemy import text
from src.models import get_session, PatientRecord, FollowUp, AccessLog


# Ensure project root is importable (so `src` package is found)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import pipeline functions and DB helpers
from src.main import run_pipeline
from src.models import get_session, PatientRecord, FollowUp, AccessLog
from src.config import OUTPUT_DIR


# ---- BEGIN PATH FIX (paste near top of app.py, after imports) ----
from pathlib import Path
# project root = folder that contains app.py
PROJECT_ROOT = Path(__file__).resolve().parent

# src folder (exists in your tree)
SRC_DIR = PROJECT_ROOT / "src"

# prefer src/output (older code), but fallback to root-level output
OUTPUT_DIR_CANDIDATES = [SRC_DIR / "output", PROJECT_ROOT / "output"]
OUTPUT_DIR = None
for p in OUTPUT_DIR_CANDIDATES:
    if p.exists():
        OUTPUT_DIR = p
        break
# if none exists yet, default to project-root/output (will be created later)
if OUTPUT_DIR is None:
    OUTPUT_DIR = PROJECT_ROOT / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use OUTPUT_DIR for file lookups
metrics_path = OUTPUT_DIR / "metrics.json"
preds_path = OUTPUT_DIR / "patient_predictions.csv"
# ---- END PATH FIX ----


st.set_page_config(page_title="Breast Cancer Demo — Dashboard", layout="wide")

st.title("Breast Cancer Demo — Research DB Dashboard")
st.write("Prototype dashboard to demonstrate anonymisation, linkage, multimodal data, and governance.")

# TOP BAR: Run pipeline / quick actions
col1, col2, col3 = st.columns([2,1,1])
with col1:
    if st.button("Run full pipeline"):
        with st.spinner("Running pipeline (ingest, anonymise, train, reports)..."):
            run_pipeline()
        st.success("Pipeline run complete. Check outputs in src/output/")

with col2:
    if st.button("Download anonymised CSV"):
        # create anonymised CSV on the fly
        session = get_session()
        rows = session.query(PatientRecord).all()
        data = []
        for r in rows:
            data.append({
                "hashed_id": r.hashed_id,
                "target": r.target,
                "mean_radius": r.mean_radius,
                "mean_texture": r.mean_texture,
                "mean_perimeter": r.mean_perimeter,
                "mean_area": r.mean_area,
                "mean_smoothness": r.mean_smoothness
            })
        session.close()
        df_an = pd.DataFrame(data)
        csv_bytes = df_an.to_csv(index=False).encode("utf-8")
        st.download_button("Download anonymised dataset (CSV)", csv_bytes, file_name=f"anonymised_breast_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')
}.csv")

with col3:
    if st.button("Download linked outcomes (CSV)"):
        session = get_session()
        # Fetch follow-up rows once, build a dict: patient_id -> (five_year_survival, chemo_received, followup_years)
        from src.models import FollowUp
        fu_rows = session.query(FollowUp.patient_id, FollowUp.five_year_survival,
                                FollowUp.chemo_received, FollowUp.followup_years).all()
        fu_map = {int(r[0]): (r[1], r[2], r[3]) for r in fu_rows}

        # join patient hashed_id with follow-up via the map (no raw SQL)
        rows = session.query(PatientRecord.patient_id, PatientRecord.hashed_id).all()
        data = []
        for pid, hid in rows:
            fu = fu_map.get(int(pid))
            data.append({
                "hashed_id": hid,
                "five_year_survival": fu[0] if fu else None,
                "chemo_received": fu[1] if fu else None,
                "followup_years": fu[2] if fu else None
            })
        session.close()
        df_linked = pd.DataFrame(data)
        st.download_button(
    "Download linked outcomes (CSV)",
    df_linked.to_csv(index=False).encode("utf-8"),
    file_name=f"linked_outcomes_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.csv"
)


st.markdown("---")

# LOAD DATABASE SNAPSHOT
session = get_session()
# read patient records into dataframe
rows = session.query(PatientRecord).all()
df_rows = pd.DataFrame([{
    "patient_id": r.patient_id,
    "hashed_id": r.hashed_id,
    "target": r.target,
    "mean_radius": r.mean_radius,
    "mean_texture": r.mean_texture,
    "mean_perimeter": r.mean_perimeter,
    "mean_area": r.mean_area,
    "mean_smoothness": r.mean_smoothness,
    "notes": (r.notes[:200] + "...") if r.notes else ""
} for r in rows])

# read linkage summary (follow_up)
# --- REPLACE raw SQL with ORM query for follow_up ---
fu_query = session.query(FollowUp.patient_id,
                         FollowUp.five_year_survival,
                         FollowUp.chemo_received,
                         FollowUp.followup_years).all()
if fu_query:
    df_fu = pd.DataFrame(fu_query, columns=['patient_id','five_year_survival','chemo_received','followup_years'])
else:
    df_fu = pd.DataFrame(columns=['patient_id','five_year_survival','chemo_received','followup_years'])
# -------------------------------------------------------

# audit log
log_rows = session.query(AccessLog).order_by(AccessLog.id.desc()).limit(50).all()
df_log = pd.DataFrame([{'id': l.id, 'user': l.user, 'action': l.action, 'ts': l.ts} for l in log_rows])
session.close()

# SUMMARY CARDS
st.subheader("Dataset summary")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Patients (rows)", len(df_rows))
with c2:
    st.metric("Malignant (target=1)", int((df_rows['target']==1).sum() if not df_rows.empty else 0))
with c3:
    st.metric("Linked follow-ups", int(len(df_fu)))
with c4:
    # compute linkage %
    link_pct = (len(df_fu) / len(df_rows) * 100) if len(df_rows) > 0 else 0.0
    st.metric("Linkage % (follow-up)", f"{link_pct:.0f}%")

# continue building UI (below)
# continued app.py (paste after previous block)

# feature means (small table)
st.subheader("Feature summary (means)")
if not df_rows.empty:
    means = df_rows[['mean_radius','mean_texture','mean_perimeter','mean_area','mean_smoothness']].mean().round(3)
    st.table(means.to_frame("mean").T)
else:
    st.write("No data yet. Run pipeline to ingest.")

st.markdown("---")

# Show metrics (if available)

st.subheader("Model metrics (pipeline output)")
if metrics_path.exists():
    try:
        metrics = json.loads(metrics_path.read_text())
        st.json(metrics)
    except Exception as e:
        st.write("Could not read metrics.json:", e)
else:
    st.write("No metrics available yet. Run pipeline to create metrics.json.")

st.markdown("---")

# Top predictions: read patient_predictions.csv if exists

st.subheader("Top predictions")
if preds_path.exists():
    df_preds = pd.read_csv(preds_path)
    # show top by probability if column exists
    prob_col = "pred_prob" if "pred_prob" in df_preds.columns else (df_preds.columns[-1] if len(df_preds.columns)>0 else None)
    if prob_col:
        st.dataframe(df_preds.sort_values(prob_col, ascending=False).head(10))
    else:
        st.dataframe(df_preds.head(10))
else:
    st.write("No predictions available yet. Run pipeline.")

st.markdown("---")

# Audit log viewer
st.subheader("Audit log (most recent entries)")
if not df_log.empty:
    st.table(df_log)
else:
    st.write("No audit log entries yet. Pipeline will log actions when run.")

st.markdown("---")

# Short auto-generated conclusion / talking points
st.subheader("Auto-generated summary & suggested talking points")
def generate_conclusion(df_rows, df_fu, metrics):
    lines = []
    n = len(df_rows)
    lines.append(f"Dataset contains {n} patient records.")
    if len(df_fu) > 0:
        lines.append(f"{len(df_fu)} records are linked to follow-up outcomes (linkage rate {link_pct:.0f}%).")
    else:
        lines.append("No follow-up linkage present (simulated HIPE table not loaded).")
    if metrics:
        sel = metrics.get('selected_model', 'N/A')
        pr = metrics.get('metrics', {}).get(sel, {}).get('pr_auc', None)
        roc = metrics.get('metrics', {}).get(sel, {}).get('roc_auc', None)
        if pr is not None and roc is not None:
            lines.append(f"Selected model: {sel}. PR-AUC={pr:.3f}, ROC-AUC={roc:.3f}.")
        else:
            lines.append("Model metrics not fully available.")
    lines.append("Notes are synthetic; hashed IDs are stored in the DB to protect privacy.")
    lines.append("Audit log demonstrates tracked access for governance.")
    lines.append("Talking points: data linkage, governance, prioritize recall in clinical models, explainability (SHAP).")
    return "\\n".join(lines)

metrics_json = None
if metrics_path.exists():
    try:
        metrics_json = json.loads(metrics_path.read_text())
    except Exception:
        metrics_json = None

conclusion_text = generate_conclusion(df_rows, df_fu, metrics_json)
st.code(conclusion_text)

st.markdown("---")
st.write("Tip: Use the Download anonymised dataset button on the top-right to provide a safe research extract for collaborators.")
