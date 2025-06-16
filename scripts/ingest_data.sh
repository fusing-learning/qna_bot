#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run the ingestion script
python -m src.ingestion.ingest

# Deactivate virtual environment
deactivate 