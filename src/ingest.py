from sklearn.datasets import load_breast_cancer
import pandas as pd
import datetime
from .models import init_db, get_session, PatientRecord, FollowUp, AccessLog
from .anonymize import hash_string
from .config import DATA_DIR

def ingest():
    init_db()
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy().reset_index(drop=True)
    session = get_session()
    for i, row in df.iterrows():
        rec = PatientRecord(
            hashed_id=hash_string(f"patient-{i+1}"),
            target=int(row['target']),
            mean_radius=float(row['mean radius']),
            mean_texture=float(row['mean texture']),
            mean_perimeter=float(row['mean perimeter']),
            mean_area=float(row['mean area']),
            mean_smoothness=float(row['mean smoothness']),
            notes=f"Synthetic note for patient {i+1}"
        )
        session.add(rec)
    session.commit()

    fu_df = pd.read_csv(DATA_DIR / 'follow_up.csv')
    for _, r in fu_df.iterrows():
        f = FollowUp(
            patient_id=int(r['patient_id']),
            five_year_survival=int(r['5yr_survival']),
            chemo_received=int(r['chemo_received']),
            followup_years=int(r['followup_years'])
        )
        session.merge(f)
    session.commit()

    log = AccessLog(user='pipeline', action='ingest', ts=str(datetime.datetime.utcnow()))
    session.add(log)
    session.commit()
    session.close()
