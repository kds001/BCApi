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


class SurveyRecordIn(BaseModel):
    respondent_id: str = Field(min_length=2, max_length=60)
    municipality: str = Field(min_length=2, max_length=80)
    age: int = Field(ge=18, le=100)
    gender: str = Field(min_length=1, max_length=20)
    preferred_candidate: str = Field(min_length=1, max_length=100)
    approval_score: float = Field(ge=0, le=100)


class SurveyRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    survey_name: str
    respondent_id: str
    municipality: str
    age: int
    gender: str
    preferred_candidate: str
    approval_score: float
    submitted_at: datetime
    firm_id: int


class SurveySummary(BaseModel):
    survey_name: str
    total_records: int
    average_approval_score: float
    candidate_distribution: dict[str, int]
    municipality_distribution: dict[str, int]
