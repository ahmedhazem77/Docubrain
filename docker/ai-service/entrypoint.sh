#!/bin/sh
set -e

cd /app

echo "Waiting for PostgreSQL..."
until python - <<'PY'
import os
import sys
import psycopg

try:
    psycopg.connect(os.environ["DATABASE_URL"])
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
do
    sleep 2
done

python setup_checkpointer.py

exec uvicorn main:app --host 0.0.0.0 --port 8000
