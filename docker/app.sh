#!/bin/bash

alembic upgrade head

cd src || { echo "Отсутствует каталог src"; exit 1; }

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000