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
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


_firm_counter = 0


def _create_firm_and_key() -> str:
    global _firm_counter
    _firm_counter += 1
    response = client.post(
        "/api/v1/encuestadoras",
        json={"name": f"BC Integrador {_firm_counter}", "contact_email": f"api{_firm_counter}@bcintegrador.com"},
    )
    assert response.status_code == 201
    return response.json()["api_key"]




def test_root_shows_active_changes():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "2.1.0"
    assert data["schema"] == "NanoEncuestaBC-v1"

def test_respuesta_schema_compatible_with_nanoencuesta():
    api_key = _create_firm_and_key()

    payload = {
        "edad": 30,
        "provincia": "Madrid",
        "ccaa": "Comunidad de Madrid",
        "nacionalidad": "Española",
        "voto_generales": "PP",
        "voto_autonomicas": "PP",
        "voto_municipales": "PP",
        "voto_europeas": "PP",
        "nota_ejecutivo": 6,
        "val_feijoo": 7,
        "val_sanchez": 4,
        "val_abascal": 3,
        "val_alvise": 2,
        "val_yolanda_diaz": 5,
        "val_irene_montero": 2,
        "val_ayuso": 8,
        "val_buxade": 2,
        "posicion_ideologica": 7,
        "voto_asociacion_juvenil": "Asociación X",
        "monarquia_republica": "Monarquía Parlamentaria",
        "division_territorial": "Sistema actual de Autonomías",
        "sistema_pensiones": "Mixto",
    }

    response = client.post("/api/v1/respuestas", headers={"X-API-Key": api_key}, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["voto_generales"] == "PP"
    assert data["encuestadora_id"] > 0


def test_lider_preferido_and_summary_endpoints():
    api_key = _create_firm_and_key()

    leader = client.post(
        "/api/v1/lideres-preferidos",
        headers={"X-API-Key": api_key},
        json={"partido": "PSOE", "lider_preferido": "Pedro Sánchez", "es_personalizado": False},
    )
    assert leader.status_code == 201

    summary = client.get("/api/v1/resumen")
    assert summary.status_code == 200
    assert "total_respuestas" in summary.json()


def test_cooldown_flow():
    ip = "203.0.113.15"

    initial = client.get(f"/api/v1/cooldown?ip_address={ip}")
    assert initial.status_code == 200
    assert initial.json()["can_vote"] is True

    record = client.post("/api/v1/cooldown/record", json={"ip_address": ip})
    assert record.status_code == 200
    assert record.json()["remaining_minutes"] == 30

    after = client.get(f"/api/v1/cooldown?ip_address={ip}")
    assert after.status_code == 200
    assert after.json()["can_vote"] is False


def test_health_includes_version_and_schema():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "2.1.0"
    assert data["schema"] == "NanoEncuestaBC-v1"
