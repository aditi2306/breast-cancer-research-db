import hashlib
from .models import get_session, PatientRecord

def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def anonymize_db():
    session = get_session()
    rows = session.query(PatientRecord).all()
    for r in rows:
        if not r.hashed_id:
            synthetic = f"patient-{r.patient_id}"
            r.hashed_id = hash_string(synthetic)
    session.commit()
    session.close()
