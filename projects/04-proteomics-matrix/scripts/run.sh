#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
CONDA_BIN="${CONDA_BIN:-/home/a/miniforge3/bin/conda}"
RUN_DIR="results/run-$(date -u +%Y%m%dT%H%M%S)-$$"
mkdir -p "$RUN_DIR"
python3 scripts/download.py > "$RUN_DIR/download.log" 2>&1
"$CONDA_BIN" run --no-capture-output -n biolearn-workflow snakemake --cores 2 --config "output_root=$RUN_DIR" > "$RUN_DIR/workflow.log" 2>&1
printf 'Report: %s/report.html\n' "$RUN_DIR"
