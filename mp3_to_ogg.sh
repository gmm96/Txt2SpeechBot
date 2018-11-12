#!/bin/bash
mod_extension="ogg"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <files>"
    exit 1
fi

dir=$(dirname "$1")
filename=$(basename "$1")
tmp_path=$(echo "$dir/tmp.ogg")
ffmpeg -i $1 -c:a libvorbis -q:a 4 $tmp_path
mv $tmp_path $1
