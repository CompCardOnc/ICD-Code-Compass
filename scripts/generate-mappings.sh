#!/usr/bin/env bash
export PYTHONPATH="src:$PYTHONPATH"
python src/icd_code_compass/mappings.py \
    --config config/index.yml \
    --output docs/mappings.json