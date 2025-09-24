#!/usr/bin/env bash
export PYTHONPATH="src:$PYTHONPATH"
python src/icd_code_compass/mappings.py \
    --config config/mappings.yml \
    --output docs/mappings.json