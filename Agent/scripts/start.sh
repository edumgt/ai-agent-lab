#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/srv/repo}"
VECTOR_DB_PATH="${VECTOR_DB_PATH:-/srv/vector_db}"
VECTOR_COLLECTION="${VECTOR_COLLECTION:-finance_agent_lab}"
PORT="${PORT:-8000}"

echo "[agent] repo_root=${REPO_ROOT}"
echo "[agent] vector_db_path=${VECTOR_DB_PATH}"

python -m app.ingest \
  --repo-root "${REPO_ROOT}" \
  --db-path "${VECTOR_DB_PATH}" \
  --collection "${VECTOR_COLLECTION}" \
  --skip-if-exists

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
