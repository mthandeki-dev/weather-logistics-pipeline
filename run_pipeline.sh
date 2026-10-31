#!/bin/bash

# Exit immediately if any script fails
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ -z "${PYTHON:-}" ]]; then
    if [[ -x .venv/bin/python ]]; then
        PYTHON=".venv/bin/python"
    else
        PYTHON="python3"
    fi
fi

echo "=== Starting Weather Logistics ETL Pipeline ==="
echo "Timestamp: $(date)"
echo "-----------------------------------------------"

# Step 1: Run Extraction
echo "Step 1/3: Extracting raw weather data..."
"$PYTHON" extract.py

# Step 2: Run Transformation
echo "Step 2/3: Transforming data and calculating risks..."
"$PYTHON" transform.py

# Step 3: Run Loading
echo "Step 3/3: Loading cleaned metrics into PostgreSQL..."
"$PYTHON" load.py

echo "-----------------------------------------------"
echo "=== Pipeline Executed Successfully! ==="