#!/usr/bin/env bash
export PYTHONPATH="src:$PYTHONPATH"
python src/icd_code_compass/labels.py \
    --config config/labels.yml \
    --output docs/labels.json