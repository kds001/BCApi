from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_firm_creation_and_submit_record_flow():
    create_firm = client.post(
        "/api/v1/encuestadoras",
        json={"name": "BC Data Lab", "contact_email": "ops@bcdatalab.com"},
    )
    assert create_firm.status_code == 201
    api_key = create_firm.json()["api_key"]

    post_record = client.post(
        "/api/v1/registros",
        headers={"X-API-Key": api_key},
        json={
            "respondent_id": "RESP-001",
            "municipality": "Mexicali",
            "age": 35,
            "gender": "F",
            "preferred_candidate": "Candidata A",
            "approval_score": 72.5,
        },
    )
    assert post_record.status_code == 201
    assert post_record.json()["survey_name"] == "#LaEncuestaBC"

    summary = client.get("/api/v1/resumen")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["total_records"] >= 1
    assert payload["candidate_distribution"]["Candidata A"] >= 1


def test_invalid_api_key_is_rejected():
    response = client.post(
        "/api/v1/registros",
        headers={"X-API-Key": "invalida"},
        json={
            "respondent_id": "RESP-002",
            "municipality": "Tijuana",
            "age": 29,
            "gender": "M",
            "preferred_candidate": "Candidato B",
            "approval_score": 55.0,
        },
    )
    assert response.status_code == 401
