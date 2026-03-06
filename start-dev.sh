#!/bin/bash

# Development startup script for FastAPI + Vue.js application

echo "Starting Weekend Overtime Management System Development..."

# Ensure database directory exists
mkdir -p backend/database

# Start backend server
echo "Starting FastAPI backend on port 8000..."
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend development server
echo "Starting Vue.js frontend on port 5173..."
cd ../frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
