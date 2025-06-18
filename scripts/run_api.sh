#!/bin/bash

# Run FastAPI backend server
echo "Starting QnA Bot FastAPI server..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the FastAPI server from project root
python -m uvicorn src.app.api:app --host 0.0.0.0 --port 8000 --reload 