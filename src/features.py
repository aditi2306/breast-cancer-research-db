import pandas as pd
from sklearn.preprocessing import StandardScaler
from .models import PatientRecord

def load_df_from_db(session):
    rows = session.query(PatientRecord).all()
    data = []
    for r in rows:
        data.append({
            'patient_id': r.patient_id,
            'hashed_id': r.hashed_id,
            'target': r.target,
            'mean_radius': r.mean_radius,
            'mean_texture': r.mean_texture,
            'mean_perimeter': r.mean_perimeter,
            'mean_area': r.mean_area,
            'mean_smoothness': r.mean_smoothness,
            'notes': r.notes
        })
    return pd.DataFrame(data)

def build_feature_matrix(df):
    X = df[['mean_radius','mean_texture','mean_perimeter','mean_area','mean_smoothness']].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    y = df['target'].astype(int).values
    return X_scaled, y, df.copy()
