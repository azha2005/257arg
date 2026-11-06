# tercera ronda: otras semillas y arranques a 0,03
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
c() { UNI_GUIA=pba25s UNI_SIG=0.01 UNI_TEMP=$3 UNI_PLAN=plan_gpba25s_$1 UNI_INICIO=$2 "$PY" distritar.py 02 --modo lla_extremo --circuitos --tol 0.02 --iter 400000 --seed $4 --workers 1 > plan_gpba25s_$1_log.txt 2>&1; }
c v1 plan_gpba25s_t3_lla_extremo_circ 0.03 8 &
c v2 plan_gpba25s_fino005_lla_extremo_circ 0.03 9 &
c v3 plan_gpba25s_lla_circ 0.05 10 &
wait; echo fin
