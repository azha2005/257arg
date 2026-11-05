#!/bin/sh
# Buenos Aires otra vez con --deptos --circuitos (escala nueva + corte temprano); max. 4 procesos
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
for grupo in "peronista_extremo lla_extremo peronista lla" "neutral proporcional"; do
  for m in $grupo; do
    sw=0.05; [ $m = lla_extremo ] && sw=0.08
    UNI_SWING=$sw nohup "$PY" distritar.py 02 --modo $m --deptos --circuitos --tol 0.02 --iter 30000 --workers 1 > plan_radios_${m}_dc_02_log.txt 2>&1 &
  done
  wait
done
echo listo
