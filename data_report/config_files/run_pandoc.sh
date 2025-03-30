#!/bin/bash
wd="$(pwd)"
name="data_report"

if [[ "$wd" != *"$name" ]]; then
    if [[ "$(pwd)" != *"$name" ]]; then
        cd "$name" || exit
    fi
    cd "config_files" || exit
fi

source="../$name.md"
metadata="meta.yaml"
dest="../$name.pdf"
rm -f "$dest"
pandoc "$source" "$metadata" -o "$dest" --pdf-engine=lualatex --citeproc
cd "$wd" || exit