#!/bin/bash
mod_extension="ogg"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <files>"
    exit 1
fi

ffmpeg -i $1 -c:a libvorbis -q:a 4 tmp.ogg
orig_name=`echo "$1" | cut -d'.' -f1`
orig_extension=`echo "$1" | cut -d'.' -f2`
mod_name="$orig_name.$mod_extension"
mv tmp.ogg $mod_name
rm $1