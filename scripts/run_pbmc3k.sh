#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
CONDA_BIN=${BIOLEARN_CONDA:-/home/a/miniforge3/bin/conda}
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMBA_NUM_THREADS=2
pbmc_out="results/pbmc3k/run-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$pbmc_out/logs" "$pbmc_out/environment" "$pbmc_out/scripts"
cp scripts/10_pbmc_prepare.py scripts/11_pbmc_seurat.R scripts/12_pbmc_scanpy.py scripts/13_pbmc_annotate.py scripts/14_pbmc_annotate_seurat.R scripts/15_pbmc_report.py scripts/16_pbmc_replot_seurat.R scripts/17_pbmc_recompute_percent.py scripts/05_bulk_manifest.py scripts/pbmc_annotation_plan.json scripts/run_pbmc3k.sh "$pbmc_out/scripts/"
: > "$pbmc_out/logs/exit-status.tsv"
run_stage() {
  local stage=$1
  shift
  local code=0
  "$@" > "$pbmc_out/logs/${stage}.log" 2>&1 || code=$?
  printf '%s\t%s\n' "$stage" "$code" >> "$pbmc_out/logs/exit-status.tsv"
  printf '%s exit=%s\n' "$stage" "$code"
  return "$code"
}
input_dir=data/pbmc3k/filtered_gene_bc_matrices/hg19
run_stage prepare "$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/10_pbmc_prepare.py "$pbmc_out"
run_stage seurat "$CONDA_BIN" run --no-capture-output -n biolearn-r Rscript scripts/11_pbmc_seurat.R "$pbmc_out/seurat" "$input_dir"
run_stage scanpy "$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/12_pbmc_scanpy.py "$pbmc_out/scanpy" "$input_dir"
run_stage annotation_python "$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/13_pbmc_annotate.py "$pbmc_out" scripts/pbmc_annotation_plan.json
run_stage annotation_r "$CONDA_BIN" run --no-capture-output -n biolearn-r Rscript scripts/14_pbmc_annotate_seurat.R "$pbmc_out"
for env in biolearn-r biolearn-py; do
  "$CONDA_BIN" list -n "$env" --json > "$pbmc_out/environment/${env}.packages.json"
  "$CONDA_BIN" list -n "$env" --explicit > "$pbmc_out/environment/${env}.linux-64.explicit.txt"
  "$CONDA_BIN" env export -n "$env" > "$pbmc_out/environment/${env}.resolved.yml"
done
run_stage report "$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/15_pbmc_report.py "$pbmc_out"
"$CONDA_BIN" run --no-capture-output -n biolearn-py python scripts/05_bulk_manifest.py "$pbmc_out"
printf '%s\n' "$pbmc_out" > results/pbmc3k/latest-run.txt
printf 'Completed: %s/acceptance.md\n' "$pbmc_out"
