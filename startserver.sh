#/bin/bash

gunicorn app.main:app --reload --bind 0.0.0.0:8020 --timeout 600 --workers 2