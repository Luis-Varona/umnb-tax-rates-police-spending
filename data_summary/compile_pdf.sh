#!/usr/bin/env bash
set -euo pipefail

NAME="data_summary"
SOURCE="$NAME.md"
METADATA="../pandoc_config/meta.yaml"
DEST="$NAME.pdf"
DEST_TEMP=$(mktemp)

CONVERTER="pandoc"
PDF_ENGINE="lualatex"
LUA_FILTER="../pandoc_config/filter.lua"
AFFILIATIONS="../pandoc_config/affiliations.tex"

for tool in "$CONVERTER" "$PDF_ENGINE" "realpath"; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo >&2 "$tool is required but not installed. Aborting..."
        exit 1
    fi
done

WD="$(pwd)"
trap 'cd "$WD"' EXIT
trap 'rm -f "$DEST_TEMP"' EXIT

if ! cd "$(dirname "$0")"; then
    echo >&2 "Failed to change to directory of script ($0). Aborting..."
    exit 1
fi

for file in "$SOURCE" "$METADATA" "$LUA_FILTER" "$AFFILIATIONS"; do
    if [ ! -f "$file" ]; then
        echo >&2 "Required configuration file $file not found. Aborting..."
        exit 1
    fi
done

echo "Compiling $SOURCE to a PDF..."

COMPILE_CMD=(
    "$CONVERTER" "$SOURCE" "$METADATA"
    -o "$DEST_TEMP" -s -C
    -f markdown+smart-implicit_figures
    -t pdf --pdf-engine="$PDF_ENGINE"
    --lua-filter="$LUA_FILTER"
    --include-before="$AFFILIATIONS"
)

if ! "${COMPILE_CMD[@]}"; then
    echo >&2 "$CONVERTER failed to generate the PDF. Aborting..."
    exit 1
fi

if [ -f "$DEST" ]; then
    echo "$DEST already exists. Overwriting..."
    rm "$DEST"
fi

if ! mv "$DEST_TEMP" "$DEST"; then
    echo >&2 "Failed to save output to $DEST. Aborting..."
    exit 1
fi

DEST_PATH="$(realpath "$DEST")"
echo "PDF compiled successfully: $DEST_PATH"
