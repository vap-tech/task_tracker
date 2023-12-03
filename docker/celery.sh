#!/bin/bash

cd src || { echo "Отсутствует каталог src"; exit 1; }

if [[ "${1}" == "celery" ]]; then
  celery --app=src.report.report:celery worker
elif [[ "${1}" == "flower" ]]; then
  celery --app=src.report.report:celery flower
 fi