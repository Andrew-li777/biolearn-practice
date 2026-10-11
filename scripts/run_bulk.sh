#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
CONDA_BIN=${BIOLEARN_CONDA:-/home/a/miniforge3/bin/conda}
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
bulk_out="results/bulk/run-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$bulk_out/logs" "$bulk_out/environment" "$bulk_out/scripts"
cp scripts/01_bulk_deseq2.R scripts/02_bulk_edger.R scripts/03_bulk_pydeseq2.py scripts/04_bulk_report.py scripts/05_bulk_manifest.py scripts/run_bulk.sh "$bulk_out/scripts/"
: > "$bulk_out/logs/exit-status.tsv"
run_stage() {
  local stage=$1
  shift
  local code=0
  "$@" > "$bulk_out/logs/${stage}.log" 2>&1 || code=$?
  printf '%s\t%s\n' "$stage" "$code" >> "$bulk_out/logs/exit-status.tsv"
  printf '%s exit=%s\n' "$stage" "$code"
  return "$code"
}
run_stage deseq2 "$CONDA_BIN" run --no-capture-output -n biolearn-r Rscript scripts/01_bulk_deseq2.R "$bulk_out"
run_stage edger "$CONDA_BIN" run --no-capture-output -n biolearn-r Rscript scripts/02_bulk_edger.R "$bulk_out"
run_stage pydeseq2 "$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/03_bulk_pydeseq2.py "$bulk_out"
for env in biolearn-r biolearn-py; do
  "$CONDA_BIN" list -n "$env" --json > "$bulk_out/environment/${env}.packages.json"
  "$CONDA_BIN" list -n "$env" --explicit > "$bulk_out/environment/${env}.linux-64.explicit.txt"
  "$CONDA_BIN" env export -n "$env" > "$bulk_out/environment/${env}.resolved.yml"
done
# Finalize the manifest after logs and exit-status have finished writing.
run_stage report "$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/04_bulk_report.py "$bulk_out"
"$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/05_bulk_manifest.py "$bulk_out"
printf '%s\n' "$bulk_out" > results/bulk/latest-run.txt
printf 'Completed: %s/acceptance.md\n' "$bulk_out"
