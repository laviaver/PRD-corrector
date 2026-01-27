#!/bin/bash
# Record backend logs to a file while you reproduce the "Internal server error".
# Run this instead of start.sh when you want to capture logs for debugging.
#
# Usage:
#   1. ./record-backend-logs.sh
#   2. In another terminal: cd frontend && npm run dev
#   3. Open http://localhost:5173, reproduce the error (Upload & Analyze)
#   4. Press Ctrl+C here to stop
#   5. Logs are in backend-session.log (and on screen)

set -e
cd "$(dirname "$0")"

LOG_FILE="${1:-backend-session.log}"
echo "Backend logs will be saved to: $LOG_FILE"
echo "Start the frontend in another terminal: cd frontend && npm run dev"
echo "Then open http://localhost:5173 and reproduce the error."
echo "Press Ctrl+C when done. Logs are in $LOG_FILE"
echo ""

cd backend
source venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee "../$LOG_FILE"
