#!/bin/bash
wd=$(pwd)
if [[ $wd != *"data_summary"* ]]; then
    cd data_summary || exit
fi
if [[ $(pwd) != *"pandoc_config" ]]; then
    cd pandoc_config || exit
fi

source="../data_summary.md"
metadata="data_summary.yaml"
dest="../data_summary.pdf"
rm -f $dest
pandoc $source $metadata -o $dest --pdf-engine=lualatex
cd "$wd" || exit