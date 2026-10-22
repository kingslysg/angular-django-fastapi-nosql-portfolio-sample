#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: ./scripts/run-demo.sh {ui|django|fastapi|graphql}

Starts one demo service. Install each Python service's requirements first;
see README.md for setup and the ports used by each service.
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

case "$1" in
  ui)
    exec python3 -m http.server 5173 --directory "$ROOT_DIR/frontend"
    ;;
  django)
    exec "$ROOT_DIR/backend/django_portal/.venv/bin/python" \
      "$ROOT_DIR/backend/django_portal/manage.py" runserver 8000
    ;;
  fastapi)
    cd "$ROOT_DIR/backend/fastapi_service"
    exec .venv/bin/python -m uvicorn main:app --reload --port 8001
    ;;
  graphql)
    cd "$ROOT_DIR/backend/graphql_gateway"
    exec .venv/bin/python -m uvicorn main:app --reload --port 8002
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
