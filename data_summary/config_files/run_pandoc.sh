#!/bin/bash
wd="$(pwd)"
if [[ "$wd" != *"config_files" ]]; then
    if [[ "$(pwd)" != *"data_summary" ]]; then
        cd "data_summary" || exit
    fi
    cd "config_files" || exit
fi

source="../data_summary.md"
metadata="meta.yaml"
dest="../data_summary.pdf"
rm -f "$dest"
pandoc "$source" "$metadata" -o "$dest" --pdf-engine=lualatex --citeproc
cd "$wd" || exit