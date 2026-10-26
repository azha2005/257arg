#!/bin/sh
# Capturas de todos los modos de un atlas: sh canton5865/capturas.sh 1962 "gan fj ucri ucrp par"
E="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
Y=$1; mkdir -p mapa$Y/img
W=$(cygpath -m "$(pwd)")    # raiz del proyecto en forma C:/...
for m in $2; do
  "$E" --headless=new --hide-scrollbars --window-size=1920,1700 --virtual-time-budget=8000 \
    --screenshot="$W/mapa$Y/img/m_$m.png" \
    "file:///$W/mapa$Y/atlas_$Y.html#bare-white-m-$m" 2>/dev/null
done
