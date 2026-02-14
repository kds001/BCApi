# BCApi

API REST para centralizar y validar la carga de resultados de **#LaEncuestaBC** por parte de múltiples encuestadoras, compatible con el esquema de `NanoEncuestaBC`.

## Compatibilidad con LaEncuestaBC

Esta API acepta exactamente el payload que envía el frontend en `dataToSubmit`:

- `edad`, `provincia`, `ccaa`, `nacionalidad`
- `voto_generales`, `voto_autonomicas`, `voto_municipales`, `voto_europeas`
- `nota_ejecutivo`, `val_feijoo`, `val_sanchez`, `val_abascal`, `val_alvise`, `val_yolanda_diaz`, `val_irene_montero`, `val_ayuso`, `val_buxade`
- `posicion_ideologica`, `voto_asociacion_juvenil`, `monarquia_republica`, `division_territorial`, `sistema_pensiones`

Además incluye:
- `POST /api/v1/lideres-preferidos` para `lideres_preferidos`.
- `GET /api/v1/cooldown` y `POST /api/v1/cooldown/record` para cooldown por IP.

## Requisitos

- Python 3.10+

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

## Endpoints

- `GET /health`
- `POST /api/v1/encuestadoras`
- `GET /api/v1/encuestadoras`
- `POST /api/v1/respuestas` (requiere `X-API-Key`)
- `GET /api/v1/respuestas`
- `POST /api/v1/lideres-preferidos` (requiere `X-API-Key`)
- `GET /api/v1/cooldown?ip_address=...`
- `POST /api/v1/cooldown/record`
- `GET /api/v1/resumen`

## Ejemplo integración (igual al frontend)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/respuestas \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: TU_API_KEY' \
  -d '{
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
    "sistema_pensiones": "Mixto"
  }'
```

Gracias a BC por permitir crear esta integración para **#LaEncuestaBC**.
