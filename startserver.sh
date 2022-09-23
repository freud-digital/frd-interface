#/bin/bash

gunicorn app.main:app --reload