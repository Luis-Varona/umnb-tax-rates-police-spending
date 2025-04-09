#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$(cd "$(dirname "$0")" && pwd)"
INITIAL_DIR="$(pwd)"
TEMP_OUT=$(mktemp)

cleanup() {
    rm -f "$TEMP_OUT"
    cd "$INITIAL_DIR"
}
trap cleanup EXIT

NAME=""
WORKING_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--name)
            NAME="$2"
            shift 2
            ;;
        -d|--directory)
            WORKING_DIR="$2"
            shift 2
            ;;
        -*)
            echo "Invalid option: $1" >&2
            exit 1
            ;;
        *)
            echo "Unexpected argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$NAME" ]]; then
    echo >&2 "Error: File stem must be provided with -n or --name."
    exit 1
fi

if [[ -z "$WORKING_DIR" ]]; then
    echo >&2 "Error: Working directory must be provided with -d or --directory."
    exit 1
fi

if ! cd "$WORKING_DIR"; then
    echo >&2 "Error: Unable to access working directory $WORKING_DIR."
    exit 1
fi

CONVERTER="pandoc"
PDF_ENGINE="lualatex"

for tool in "$CONVERTER" "$PDF_ENGINE"; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo >&2 "Error: $tool is required but not installed."
        exit 1
    fi
done

SOURCE="$NAME.md"
DEST="$NAME.pdf"
METADATA="$CONFIG_DIR/meta.yaml"
LUA_FILTER="$CONFIG_DIR/filter.lua"
AFFILIATIONS="$CONFIG_DIR/affiliations.tex"

for file in "$SOURCE" "$METADATA" "$LUA_FILTER" "$AFFILIATIONS"; do
    if [ ! -f "$file" ]; then
        echo >&2 "Error: Required configuration file $file not found."
        exit 1
    fi
done

echo "Compiling $SOURCE to a PDF..."

COMPILE_CMD=(
    "$CONVERTER" "$SOURCE" "$METADATA"
    -o "$TEMP_OUT" -s -C
    -f markdown+smart-implicit_figures
    -t pdf --pdf-engine="$PDF_ENGINE"
    --lua-filter="$LUA_FILTER"
    --include-before="$AFFILIATIONS"
)

if ! "${COMPILE_CMD[@]}"; then
    echo >&2 "Error: $CONVERTER failed to generate the PDF."
    exit 1
fi

if [ -f "$DEST" ]; then
    echo "$DEST already exists. Overwriting..."
fi

if ! mv -f "$TEMP_OUT" "$DEST"; then
    echo >&2 "Error: Failed to save output to $DEST."
    exit 1
fi

DEST_PATH="$(cd "$(dirname "$DEST")" && pwd)/$(basename "$DEST")"
echo "PDF compiled successfully: $DEST_PATH"
