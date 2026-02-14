import secrets
from collections import Counter

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import PollingFirm, SurveyRecord
from .schemas import (
    PollingFirmCreate,
    PollingFirmCreated,
    PollingFirmOut,
    SurveyRecordIn,
    SurveyRecordOut,
    SurveySummary,
)

app = FastAPI(
    title="BCApi",
    description="API para integrar datos de #LaEncuestaBC desde múltiples encuestadoras.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

SURVEY_NAME = "#LaEncuestaBC"


def get_firm_by_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> PollingFirm:
    firm = db.query(PollingFirm).filter(PollingFirm.api_key == x_api_key).first()
    if not firm:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida")
    return firm


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "BCApi"}


@app.post("/api/v1/encuestadoras", response_model=PollingFirmCreated, status_code=status.HTTP_201_CREATED)
def create_polling_firm(payload: PollingFirmCreate, db: Session = Depends(get_db)) -> PollingFirm:
    firm = PollingFirm(
        name=payload.name.strip(),
        contact_email=payload.contact_email,
        api_key=secrets.token_hex(24),
    )
    db.add(firm)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="La encuestadora o correo ya existe")
    db.refresh(firm)
    return firm


@app.get("/api/v1/encuestadoras", response_model=list[PollingFirmOut])
def list_polling_firms(db: Session = Depends(get_db)) -> list[PollingFirm]:
    return db.query(PollingFirm).order_by(PollingFirm.created_at.desc()).all()


@app.post("/api/v1/registros", response_model=SurveyRecordOut, status_code=status.HTTP_201_CREATED)
def submit_record(
    payload: SurveyRecordIn,
    firm: PollingFirm = Depends(get_firm_by_api_key),
    db: Session = Depends(get_db),
) -> SurveyRecord:
    record = SurveyRecord(
        survey_name=SURVEY_NAME,
        respondent_id=payload.respondent_id,
        municipality=payload.municipality,
        age=payload.age,
        gender=payload.gender,
        preferred_candidate=payload.preferred_candidate,
        approval_score=payload.approval_score,
        firm_id=firm.id,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Este respondiente ya fue enviado por esta encuestadora")
    db.refresh(record)
    return record


@app.get("/api/v1/registros", response_model=list[SurveyRecordOut])
def list_records(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[SurveyRecord]:
    return (
        db.query(SurveyRecord)
        .filter(SurveyRecord.survey_name == SURVEY_NAME)
        .order_by(SurveyRecord.submitted_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@app.get("/api/v1/resumen", response_model=SurveySummary)
def survey_summary(db: Session = Depends(get_db)) -> SurveySummary:
    records = db.query(SurveyRecord).filter(SurveyRecord.survey_name == SURVEY_NAME).all()
    total = len(records)
    if total == 0:
        return SurveySummary(
            survey_name=SURVEY_NAME,
            total_records=0,
            average_approval_score=0,
            candidate_distribution={},
            municipality_distribution={},
        )

    avg_approval = round(sum(record.approval_score for record in records) / total, 2)
    candidates = Counter(record.preferred_candidate for record in records)
    municipalities = Counter(record.municipality for record in records)

    return SurveySummary(
        survey_name=SURVEY_NAME,
        total_records=total,
        average_approval_score=avg_approval,
        candidate_distribution=dict(candidates),
        municipality_distribution=dict(municipalities),
    )
