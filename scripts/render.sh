#!/usr/bin/env bash
# Renders the Helm chart into gitops/base/manifests.yaml.
# The release name "internal-service" ensures resource names are stable
# and match the names referenced in the Kustomize overlay patches.
#
# Usage:
#   ./scripts/render.sh [extra helm --set flags]
#
# Example:
#   ./scripts/render.sh --set hub=docker.io/myorg --set tag=1.2.3

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHART_DIR="${ROOT_DIR}/charts/internal-service"
OUTPUT="${ROOT_DIR}/gitops/base/manifests.yaml"

helm template internal-service "${CHART_DIR}" \
  --set prod=false \
  "$@" \
  > "${OUTPUT}"

echo "Rendered manifests written to ${OUTPUT}"
