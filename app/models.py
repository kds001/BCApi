from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class PollingFirm(Base):
    __tablename__ = "polling_firms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Respuesta(Base):
    __tablename__ = "respuestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    provincia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ccaa: Mapped[str | None] = mapped_column(String(80), nullable=True)
    nacionalidad: Mapped[str | None] = mapped_column(String(80), nullable=True)

    voto_generales: Mapped[str | None] = mapped_column(String(120), nullable=True)
    voto_autonomicas: Mapped[str | None] = mapped_column(String(120), nullable=True)
    voto_municipales: Mapped[str | None] = mapped_column(String(120), nullable=True)
    voto_europeas: Mapped[str | None] = mapped_column(String(120), nullable=True)

    nota_ejecutivo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    val_feijoo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_sanchez: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_abascal: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_alvise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_yolanda_diaz: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_irene_montero: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_ayuso: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    val_buxade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    posicion_ideologica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    voto_asociacion_juvenil: Mapped[str | None] = mapped_column(String(160), nullable=True)
    monarquia_republica: Mapped[str | None] = mapped_column(String(120), nullable=True)
    division_territorial: Mapped[str | None] = mapped_column(String(180), nullable=True)
    sistema_pensiones: Mapped[str | None] = mapped_column(String(120), nullable=True)

    encuestadora_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class LiderPreferido(Base):
    __tablename__ = "lideres_preferidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partido: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lider_preferido: Mapped[str] = mapped_column(String(120), nullable=False)
    es_personalizado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encuestadora_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class VotingCooldown(Base):
    __tablename__ = "voting_cooldowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    last_vote_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
