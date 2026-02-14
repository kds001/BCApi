# BCApi

API REST para centralizar y validar la carga de resultados de la encuesta **#LaEncuestaBC** por parte de múltiples encuestadoras.

## Características

- Registro de encuestadoras con generación automática de API key.
- Ingesta de registros individuales protegida por `X-API-Key`.
- Listado paginado de registros cargados.
- Resumen agregado (total de registros, promedio de aprobación y distribuciones).
- Documentación interactiva automática en `/docs`.

## Requisitos

- Python 3.11+

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

## Endpoints principales

- `GET /health`
- `POST /api/v1/encuestadoras`
- `GET /api/v1/encuestadoras`
- `POST /api/v1/registros` (requiere header `X-API-Key`)
- `GET /api/v1/registros?limit=100&offset=0`
- `GET /api/v1/resumen`

## Ejemplo rápido

1. Crear encuestadora:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/encuestadoras \
  -H 'Content-Type: application/json' \
  -d '{"name":"Encuestadora BC","contact_email":"contacto@encuestadorabc.mx"}'
```

2. Enviar registro:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/registros \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: TU_API_KEY' \
  -d '{
    "respondent_id":"RESP-1001",
    "municipality":"Ensenada",
    "age":42,
    "gender":"F",
    "preferred_candidate":"Candidata A",
    "approval_score":67.8
  }'
```

Gracias a BC por permitir crear esta integración para **#LaEncuestaBC**.
