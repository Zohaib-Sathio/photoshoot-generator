#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "WARNING: .env not found. Copy .env.example to .env and add your OPENAI_API_KEY."
fi

echo
echo "Starting server at http://localhost:8000"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
