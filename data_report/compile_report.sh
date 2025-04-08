#!/usr/bin/env bash
set -euo pipefail

INITIAL_DIR="$(pwd)"
trap 'cd "$INITIAL_DIR"' EXIT

MAIN="../pandoc_config/compile_pdf.sh"
NAME="data_report"
WORKING_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$WORKING_DIR"
bash "$MAIN" -n "$NAME" -d "$WORKING_DIR"
