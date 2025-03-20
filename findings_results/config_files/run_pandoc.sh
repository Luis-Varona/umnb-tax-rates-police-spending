#!/bin/bash
wd="$(pwd)"
if [[ "$wd" != *"config_files" ]]; then
    if [[ "$(pwd)" != *"findings_results" ]]; then
        cd "findings_results" || exit
    fi
    cd "config_files" || exit
fi

source="../findings_results.md"
metadata="meta.yaml"
dest="../findings_results.pdf"
rm -f "$dest"
pandoc "$source" "$metadata" -o "$dest" --pdf-engine=lualatex --citeproc
cd "$wd" || exit