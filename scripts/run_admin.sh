#!/bin/bash

# Run the Streamlit admin interface
echo "Starting QnA Bot Admin Interface..."
echo "Make sure the FastAPI backend is running on http://localhost:8000"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run Streamlit admin interface
cd "$(dirname "$0")/.."
streamlit run src/ui/admin.py --server.port 8501 --server.address 0.0.0.0 