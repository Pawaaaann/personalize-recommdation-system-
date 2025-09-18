#!/bin/bash

# Start the backend API server in the background
echo "Starting backend API server..."
python -m uvicorn src.edurec.api.main:app --host localhost --port 8000 --reload &

# Give the backend time to start
sleep 3

# Start the frontend development server
echo "Starting frontend development server..."
cd frontend && npx vite --host 0.0.0.0 --port 5000