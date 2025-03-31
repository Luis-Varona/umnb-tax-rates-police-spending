#!/usr/bin/env bash
wd="$(pwd)"
cd "$(dirname "$0")" || exit

name="data_report"
source="$name.md"
metadata="config_files/meta.yaml"
dest="$name.pdf"

rm -f "$dest"
pandoc -s -C -f markdown-implicit_figures -t pdf --pdf-engine=lualatex \
    "$source" "$metadata" -o "$dest"
cd "$wd" || exit