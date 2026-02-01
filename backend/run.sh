#!/bin/bash
# Run the backend server. Use this if "uvicorn" command is not found.
# From project root: ./backend/run.sh
# Or from backend/: ./run.sh

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
source venv/bin/activate

# Use python -m uvicorn so it works even when uvicorn is not on PATH
exec python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
