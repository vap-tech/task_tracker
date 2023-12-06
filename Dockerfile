FROM python:3.10-slim-buster

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY pyproject.toml .

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

RUN chmod a+x docker/*.sh

# RUN alembic upgrade head

# WORKDIR src

# CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000