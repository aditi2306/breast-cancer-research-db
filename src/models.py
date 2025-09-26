from sqlalchemy.orm import declarative_base, Session, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, create_engine

Base = declarative_base()

class PatientRecord(Base):
    __tablename__ = "patient_records"
    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hashed_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    target: Mapped[int] = mapped_column(Integer)
    mean_radius: Mapped[float] = mapped_column(Float)
    mean_texture: Mapped[float] = mapped_column(Float)
    mean_perimeter: Mapped[float] = mapped_column(Float)
    mean_area: Mapped[float] = mapped_column(Float)
    mean_smoothness: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(String(2000), nullable=True)

class FollowUp(Base):
    __tablename__ = "follow_up"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer)
    five_year_survival: Mapped[int] = mapped_column(Integer)
    chemo_received: Mapped[int] = mapped_column(Integer)
    followup_years: Mapped[int] = mapped_column(Integer)

class AccessLog(Base):
    __tablename__ = "access_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(256))
    ts: Mapped[str] = mapped_column(String(64))

from .config import DB_URL
engine = create_engine(DB_URL, echo=False, future=True)

def init_db():
    Base.metadata.create_all(engine)
    return engine

def get_session():
    return Session(engine)
