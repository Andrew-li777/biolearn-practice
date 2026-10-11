#!/usr/bin/env bash
set -u
cd /home/a/projects/biolearn-practice
mkdir -p environment/logs environment/validation
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMBA_NUM_THREADS=2
CONDA=/home/a/miniforge3/bin/conda
status=0
run_check() {
  local name=$1
  shift
  "$@" > "environment/logs/${name}.log" 2>&1
  local result=$?
  printf '%s exit=%s\n' "$name" "$result" | tee -a environment/validation/status.txt
  if (( result )); then status=1; fi
}
: > environment/validation/status.txt
run_check verify-r "$CONDA" run --no-capture-output -n biolearn-r Rscript environment/validation/verify.R
run_check verify-python "$CONDA" run --no-capture-output -n biolearn-py python environment/validation/verify.py
run_check verify-pbmc3k-r "$CONDA" run --no-capture-output -n biolearn-r Rscript environment/validation/verify-pbmc3k.R
run_check verify-pbmc3k-python "$CONDA" run --no-capture-output -n biolearn-py python environment/validation/verify-pbmc3k.py
for env in biolearn-r biolearn-py; do
  "$CONDA" env export -n "$env" > "environment/${env}.resolved.yml"
  "$CONDA" list -n "$env" --explicit > "environment/${env}.linux-64.explicit.txt"
  "$CONDA" list -n "$env" --json > "environment/${env}.packages.json"
done
exit "$status"
