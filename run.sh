#!/bin/bash
# Run both backend (FastAPI) and frontend (Vite) from project root

# Start backend
cd backend || exit 1
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend || exit 1
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Backend running (PID $BACKEND_PID), Frontend running (PID $FRONTEND_PID)"
echo "Press [CTRL+C] to stop both."

# Wait for both to finish
wait $BACKEND_PID $FRONTEND_PID
