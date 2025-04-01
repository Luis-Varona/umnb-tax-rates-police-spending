#!/usr/bin/env bash
wd="$(pwd)"
cd "$(dirname "$0")" || exit

name="data_summary"
source="$name.md"
metadata="config_files/meta.yaml"
dest="$name.pdf"

rm -f "$dest"
pandoc -s -C -f markdown+smart-implicit_figures -t pdf --pdf-engine=lualatex \
    "$source" "$metadata" -o "$dest"
cd "$wd" || exit