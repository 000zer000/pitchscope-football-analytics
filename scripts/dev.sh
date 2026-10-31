#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work
export NPM_CONFIG_CACHE="${NPM_CONFIG_CACHE:-$PWD/work/npm-cache}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/work/uv-cache}"
export PYTHONPATH=backend
export PGPORT="${PGPORT:-55432}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://postgres:postgres@127.0.0.1:$PGPORT/pitchscope}"
export DB_POOL_SIZE=1
uv sync --frozen
[ -d scripts/local-db/node_modules ] || npm ci --prefix scripts/local-db
[ -d frontend/node_modules ] || npm ci --prefix frontend
PGLITE_DATA="$PWD/work/pglite" node scripts/local-db/server.mjs > work/local-db.log 2>&1 &
dbpid=$!
apipid='';webpid=''
cleanup() { for pid in "$webpid" "$apipid" "$dbpid"; do [ -z "$pid" ] || kill "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM
for i in $(seq 1 30); do
  if ! kill -0 "$dbpid" 2>/dev/null; then
    cat work/local-db.log >&2
    echo "Local database failed to start. Choose a free PGPORT; existing services were left untouched." >&2
    exit 1
  fi
  if .venv/bin/python -c 'from app.db import engine; engine.connect().close()' 2>/dev/null; then break; fi
  sleep 1
done
.venv/bin/alembic upgrade head
if [ -f data/raw/data/matches/43/106.json ]; then
  .venv/bin/python -m app.ingest import > work/start-import.log
fi
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 > work/api.log 2>&1 &
apipid=$!
pushd frontend >/dev/null
node node_modules/vite/bin/vite.js --host 127.0.0.1 &
webpid=$!
popd >/dev/null
printf 'PitchScope local: http://127.0.0.1:5173 (Ctrl+C to stop)\n'
wait "$webpid"
