from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PollingFirmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    contact_email: EmailStr


class PollingFirmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_email: EmailStr
    created_at: datetime


class PollingFirmCreated(PollingFirmOut):
    api_key: str


class RespuestaIn(BaseModel):
    edad: int = Field(ge=14, le=100)
    provincia: str | None = None
    ccaa: str | None = None
    nacionalidad: str | None = None
    voto_generales: str | None = None
    voto_autonomicas: str | None = None
    voto_municipales: str | None = None
    voto_europeas: str | None = None
    nota_ejecutivo: int | None = Field(default=None, ge=0, le=10)
    val_feijoo: int = Field(ge=0, le=10)
    val_sanchez: int = Field(ge=0, le=10)
    val_abascal: int = Field(ge=0, le=10)
    val_alvise: int = Field(ge=0, le=10)
    val_yolanda_diaz: int = Field(ge=0, le=10)
    val_irene_montero: int = Field(ge=0, le=10)
    val_ayuso: int = Field(ge=0, le=10)
    val_buxade: int = Field(ge=0, le=10)
    posicion_ideologica: int | None = Field(default=None, ge=1, le=10)
    voto_asociacion_juvenil: str | None = None
    monarquia_republica: str | None = None
    division_territorial: str | None = None
    sistema_pensiones: str | None = None


class RespuestaOut(RespuestaIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    encuestadora_id: int
    created_at: datetime


class LiderPreferidoIn(BaseModel):
    partido: str | None = None
    lider_preferido: str = Field(min_length=1, max_length=120)
    es_personalizado: bool = False


class LiderPreferidoOut(LiderPreferidoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    encuestadora_id: int
    created_at: datetime


class CooldownCheck(BaseModel):
    can_vote: bool
    remaining_minutes: int


class CooldownRecordIn(BaseModel):
    ip_address: str = Field(min_length=3, max_length=64)


class ResumenOut(BaseModel):
    total_respuestas: int
    promedio_nota_ejecutivo: float
    promedio_posicion_ideologica: float
    distribucion_voto_general: dict[str, int]
    distribucion_ccaa: dict[str, int]
