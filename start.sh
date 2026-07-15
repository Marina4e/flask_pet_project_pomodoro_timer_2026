#!/usr/bin/env sh
set -e

flask --app run.py db upgrade

exec gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  "app:create_app()"
