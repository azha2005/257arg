#!/bin/sh
# cola: rehace por circuitos los planes de limites libres (despues de los extremos); max. 4 procesos
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
until grep -q '^[0-9]* s$' plan_radios_peronista_extremo_circ_log.txt && grep -q '^[0-9]* s$' plan_radios_lla_extremo_circ_log.txt; do sleep 30; done
for par in "neutral proporcional" "peronista lla"; do
  for m in $par; do
    nohup "$PY" distritar.py --modo $m --circuitos --tol 0.02 --iter 30000 --workers 2 > plan_radios_${m}_circ_log.txt 2>&1 &
  done
  wait
done
echo listo
