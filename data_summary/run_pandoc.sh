#!/usr/bin/env bash
wd="$(pwd)"
cd "$(dirname "$0")" || exit

name="data_summary"
source="$name.md"
metadata="config_files/meta.yaml"
dest="$name.pdf"

rm -f "$dest"
pandoc "$source" "$metadata" -o "$dest" --pdf-engine=lualatex --citeproc
cd "$wd" || exit