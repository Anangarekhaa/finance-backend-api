#!/bin/bash
alembic upgrade head
python -m seed
uvicorn app.main:app --host 0.0.0.0 --port 8000
