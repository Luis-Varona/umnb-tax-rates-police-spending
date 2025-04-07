#!/usr/bin/env bash
command -v pandoc >/dev/null 2>&1 || \
    { echo >&2 "Pandoc is required but not installed. Aborting."; exit 1; }
command -v lualatex >/dev/null 2>&1 || \
    { echo >&2 "LuaLaTeX is required but not installed. Aborting."; exit 1; }

wd="$(pwd)"
trap 'cd "$wd"' EXIT
cd "$(dirname "$0")" || exit

name="data_summary"
source="$name.md"
metadata="config_files/meta.yaml"
dest="$name.pdf"

rm -f "$dest"
pandoc -s -C -f markdown+smart-implicit_figures -t pdf --pdf-engine=lualatex \
    "$source" "$metadata" -o "$dest"
