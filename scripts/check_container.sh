#!/usr/bin/env bash
set -euo pipefail
out=${1:-environment/nfcore/container-check}
mkdir -p "$out"
trap 'code=$?; printf "FAIL exit=%s\n" "$code" > "$out/status.txt"' ERR
docker version > "$out/version.txt" 2>&1
docker info > "$out/engine.txt" 2>&1
# Inherit existing client proxy variables; do not write or modify proxy configuration.
docker pull alpine:3.20 > "$out/pull.log" 2>&1
docker image inspect alpine:3.20 --format '{{json .RepoDigests}}' > "$out/image-digests.json"
docker run --rm alpine:3.20 nslookup raw.githubusercontent.com > "$out/runtime-dns.log" 2>&1
# BusyBox wget returned HTTP503 through the existing proxy while curl's HTTPS
# CONNECT succeeds. Test with curl without changing daemon or system proxies.
docker pull docker.io/curlimages/curl:8.10.1 > "$out/curl-pull.log" 2>&1
docker image inspect docker.io/curlimages/curl:8.10.1 > "$out/curl-image.json"
docker run --rm -e HTTP_PROXY -e HTTPS_PROXY -e http_proxy -e https_proxy docker.io/curlimages/curl:8.10.1 \
  --fail --location --connect-timeout 15 --max-time 60 --output /dev/null \
  --write-out 'http_code=%{http_code} bytes=%{size_download}\n' \
  https://raw.githubusercontent.com/nf-core/test-datasets/626c8fab639062eade4b10747e919341cbf9b41a/samplesheet/v3.10/samplesheet_test.csv > "$out/runtime-network.log" 2>&1
printf 'PASS\n' > "$out/status.txt"
