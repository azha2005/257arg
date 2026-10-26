#!/bin/bash
# Captura del poster (1920x1649) con Edge headless.
#   shot.sh <atlas.html> <salida.png> [hash]
# hash: "bare" = solo el poster sobre fondo negro (para comparar con cmp.ps1 -Cmd shift)
#       "bare-white" = idem sobre blanco; agregar "-m-<id>" para elegir el modo (p. ej. bare-white-m-r2d)
H="${3:-bare}"
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
"$EDGE" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=20000 --window-size=1920,1649 \
  --screenshot="$(cygpath -w "$2")" "file:///$(cygpath -m "$1")#$H" 2>&1 | grep -i written
