#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
VENV_PIP="$PROJECT_DIR/venv/bin/pip"
VENV_ALEMBIC="$PROJECT_DIR/venv/bin/alembic"
VENV_UVICORN="$PROJECT_DIR/venv/bin/uvicorn"

# Create virtual environment if missing
if [ ! -d "venv" ]; then
  echo "[setup] Creating virtual environment..."
  python3 -m venv venv
fi

# Install dependencies
echo "[setup] Installing dependencies..."
"$VENV_PIP" install -r requirements.txt -q

# Check .env file
if [ ! -f ".env" ]; then
  echo "[error] .env file not found. Please create one. See CLAUDE.md for required variables."
  exit 1
fi

# Run DB migrations
echo "[db] Running Alembic migrations..."
"$VENV_ALEMBIC" upgrade head

# Start server
echo "[server] Starting API server at http://localhost:8000"
"$VENV_UVICORN" app.main:app --reload --host 0.0.0.0 --port 8000