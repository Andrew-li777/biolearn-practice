#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
conda_bin=${BIOLEARN_CONDA:-/home/a/miniforge3/bin/conda}
nf_out=${1:-results/nfcore/rnaseq-3.27.0-test}
if [[ -d "$nf_out" ]] && [[ -n "$(ls -A "$nf_out")" ]]; then
  printf 'Refusing to overwrite existing attempt: %s\n' "$nf_out" >&2
  exit 2
fi
mkdir -p "$nf_out" logs/nfcore
expected=a1fcdddd3b826fe46eb46f0479f2ff8a7815af05
actual=$(git -C workflow/nfcore-rnaseq-3.27.0 rev-parse HEAD)
test "$actual" = "$expected"
printf '%s\n' "$actual" > "$nf_out/pipeline-commit.txt"
cp workflow/nfcore-vm.config "$nf_out/"
cp scripts/run_nfcore_test.sh scripts/nfcore_status.py "$nf_out/"
date -u +%FT%TZ > "$nf_out/started-at.txt"
code=0
if ! docker info > "$nf_out/container-preflight.log" 2>&1; then
  cp "$nf_out/container-preflight.log" "$nf_out/console.log"
  printf '127\n' > "$nf_out/exit-code.txt"
  python3 scripts/nfcore_status.py "$nf_out"
  exit 127
fi
"$conda_bin" run --no-capture-output -n biolearn-workflow nextflow -log "$nf_out/nextflow.log" run ./workflow/nfcore-rnaseq-3.27.0 -profile test,docker -c workflow/nfcore-vm.config --outdir "$nf_out/output" -work-dir "$nf_out/work" -with-report "$nf_out/execution-report.html" -with-trace "$nf_out/execution-trace.tsv" -with-timeline "$nf_out/execution-timeline.html" -ansi-log false -resume > "$nf_out/console.log" 2>&1 || code=$?
printf '%s\n' "$code" > "$nf_out/exit-code.txt"
date -u +%FT%TZ > "$nf_out/ended-at.txt"
python3 scripts/nfcore_status.py "$nf_out"
exit "$code"
