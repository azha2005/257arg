# gerrymanders antiperonistas guiados por elecciones viejas (pluralidad); antes: 2015p+2011p y 2015+2015b, ahora 2019p y 2019
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
corre() { UNI_GUIA=$1 UNI_PLAN=plan_g$1 UNI_INICIO=plan_radios_lla_extremo_circ UNI_SWING=0.05 "$PY" distritar.py --modo lla_extremo --circuitos --tol 0.02 --iter 30000 --workers 2 > plan_g$1_log.txt 2>&1; }
(corre 2019p) &
(corre 2019) &
wait; echo fin
