from .ingest import ingest
from .anonymize import anonymize_db
from .models import get_session
from .features import load_df_from_db, build_feature_matrix
from .train import train_and_eval

def run_pipeline():
    ingest()
    anonymize_db()
    session = get_session()
    df = load_df_from_db(session)
    X, y, df_all = build_feature_matrix(df)
    results = train_and_eval(X, y)
    print("Results:", results)
    session.close()

if __name__ == '__main__':
    run_pipeline()
