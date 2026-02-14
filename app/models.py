from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class PollingFirm(Base):
    __tablename__ = "polling_firms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    records: Mapped[list["SurveyRecord"]] = relationship(back_populates="firm", cascade="all, delete-orphan")


class SurveyRecord(Base):
    __tablename__ = "survey_records"
    __table_args__ = (
        UniqueConstraint("firm_id", "respondent_id", name="uq_firm_respondent"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    survey_name: Mapped[str] = mapped_column(String(80), default="#LaEncuestaBC", nullable=False)
    respondent_id: Mapped[str] = mapped_column(String(60), nullable=False)
    municipality: Mapped[str] = mapped_column(String(80), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    preferred_candidate: Mapped[str] = mapped_column(String(100), nullable=False)
    approval_score: Mapped[float] = mapped_column(Float, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    firm_id: Mapped[int] = mapped_column(ForeignKey("polling_firms.id"), nullable=False)
    firm: Mapped[PollingFirm] = relationship(back_populates="records")
