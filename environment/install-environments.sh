#!/usr/bin/env bash
set -euo pipefail
# Flat repodata avoids the shard timeout observed during this installation.
export MAMBA_USE_SHARDED_REPODATA=false
cd /home/a/projects/biolearn-practice
MAMBA=/home/a/miniforge3/bin/mamba
"$MAMBA" env create --yes --strict-channel-priority -f environment/r-analysis.yml > environment/logs/install-r.log 2>&1 &
r_pid=$!
"$MAMBA" env create --yes --strict-channel-priority -f environment/python-analysis.yml > environment/logs/install-python.log 2>&1 &
p_pid=$!
r_status=0
p_status=0
wait "$r_pid" || r_status=$?
wait "$p_pid" || p_status=$?
printf 'R install exit=%s\nPython install exit=%s\n' "$r_status" "$p_status"
if (( r_status || p_status )); then exit 1; fi
