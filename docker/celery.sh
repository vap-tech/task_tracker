#!/bin/bash

#cd fastapi_app || { echo "Отсутствует каталог fastapi_app"; exit 1; }

if [[ "${1}" == "celery" ]]; then
  celery --app=src.report.report:celery worker
elif [[ "${1}" == "flower" ]]; then
  celery --app=src.report.report:celery flower
 fi