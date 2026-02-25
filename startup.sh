#!/bin/bash
set -e 

echo "🚀 Step 1: Generating data..."
python scripts/generate_data.py

echo "🚀 Step 2: Running main application..."
python src/main.py

echo "🚀 Step 3: Running tests..."
python scripts/test.py

echo "✅ All steps completed!"