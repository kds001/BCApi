import secrets
from collections import Counter
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import LiderPreferido, PollingFirm, Respuesta, VotingCooldown
from .schemas import (
    CooldownCheck,
    CooldownRecordIn,
    LiderPreferidoIn,
    LiderPreferidoOut,
    PollingFirmCreate,
    PollingFirmCreated,
    PollingFirmOut,
    RespuestaIn,
    RespuestaOut,
    ResumenOut,
)

app = FastAPI(
    title="BCApi",
    description="API para integrar datos de #LaEncuestaBC desde múltiples encuestadoras.",
    version="2.0.0",
)

Base.metadata.create_all(bind=engine)
COOLDOWN_MINUTES = 30


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


@app.post("/api/v1/respuestas", response_model=RespuestaOut, status_code=status.HTTP_201_CREATED)
def create_respuesta(
    payload: RespuestaIn,
    firm: PollingFirm = Depends(get_firm_by_api_key),
    db: Session = Depends(get_db),
) -> Respuesta:
    respuesta = Respuesta(**payload.model_dump(), encuestadora_id=firm.id)
    db.add(respuesta)
    db.commit()
    db.refresh(respuesta)
    return respuesta


@app.get("/api/v1/respuestas", response_model=list[RespuestaOut])
def list_respuestas(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Respuesta]:
    return db.query(Respuesta).order_by(Respuesta.created_at.desc()).offset(offset).limit(limit).all()


@app.post("/api/v1/lideres-preferidos", response_model=LiderPreferidoOut, status_code=status.HTTP_201_CREATED)
def create_lider_preferido(
    payload: LiderPreferidoIn,
    firm: PollingFirm = Depends(get_firm_by_api_key),
    db: Session = Depends(get_db),
) -> LiderPreferido:
    lider = LiderPreferido(**payload.model_dump(), encuestadora_id=firm.id)
    db.add(lider)
    db.commit()
    db.refresh(lider)
    return lider


@app.get("/api/v1/cooldown", response_model=CooldownCheck)
def check_cooldown(ip_address: str = Query(..., min_length=3, max_length=64), db: Session = Depends(get_db)) -> CooldownCheck:
    row = db.query(VotingCooldown).filter(VotingCooldown.ip_address == ip_address).first()
    if not row:
        return CooldownCheck(can_vote=True, remaining_minutes=0)

    elapsed = datetime.utcnow() - row.last_vote_at
    remaining = timedelta(minutes=COOLDOWN_MINUTES) - elapsed
    if remaining.total_seconds() <= 0:
        return CooldownCheck(can_vote=True, remaining_minutes=0)

    remaining_minutes = int(remaining.total_seconds() // 60) + 1
    return CooldownCheck(can_vote=False, remaining_minutes=remaining_minutes)


@app.post("/api/v1/cooldown/record", response_model=CooldownCheck)
def record_cooldown(payload: CooldownRecordIn, db: Session = Depends(get_db)) -> CooldownCheck:
    now = datetime.utcnow()
    row = db.query(VotingCooldown).filter(VotingCooldown.ip_address == payload.ip_address).first()

    if row:
        row.last_vote_at = now
    else:
        row = VotingCooldown(ip_address=payload.ip_address, last_vote_at=now)
        db.add(row)

    db.commit()
    return CooldownCheck(can_vote=False, remaining_minutes=COOLDOWN_MINUTES)


@app.get("/api/v1/resumen", response_model=ResumenOut)
def get_resumen(db: Session = Depends(get_db)) -> ResumenOut:
    respuestas = db.query(Respuesta).all()
    if not respuestas:
        return ResumenOut(
            total_respuestas=0,
            promedio_nota_ejecutivo=0,
            promedio_posicion_ideologica=0,
            distribucion_voto_general={},
            distribucion_ccaa={},
        )

    total = len(respuestas)
    notas = [r.nota_ejecutivo for r in respuestas if r.nota_ejecutivo is not None]
    ideologia = [r.posicion_ideologica for r in respuestas if r.posicion_ideologica is not None]

    votos = Counter(r.voto_generales for r in respuestas if r.voto_generales)
    ccaa = Counter(r.ccaa for r in respuestas if r.ccaa)

    return ResumenOut(
        total_respuestas=total,
        promedio_nota_ejecutivo=round(sum(notas) / len(notas), 2) if notas else 0,
        promedio_posicion_ideologica=round(sum(ideologia) / len(ideologia), 2) if ideologia else 0,
        distribucion_voto_general=dict(votos),
        distribucion_ccaa=dict(ccaa),
    )
