#!/bin/bash

IFS=.: read -r _ h m s _ < <(ffmpeg -i "$1" 2>&1 | grep Duration);echo $(( h * 3600 + m * 60 + s ));