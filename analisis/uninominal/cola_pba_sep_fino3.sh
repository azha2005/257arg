# segunda ronda desde t2 (la mejor): mas caliente y mas larga
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
c() { UNI_GUIA=pba25s UNI_SIG=0.01 UNI_TEMP=$3 UNI_PLAN=plan_gpba25s_$1 UNI_INICIO=$2 "$PY" distritar.py 02 --modo lla_extremo --circuitos --tol 0.02 --iter 600000 --seed $4 --workers 1 > plan_gpba25s_$1_log.txt 2>&1; }
c u1 plan_gpba25s_t2_lla_extremo_circ 0.03 5 &
c u2 plan_gpba25s_t2_lla_extremo_circ 0.08 6 &
c u3 plan_gpba25s_t2_lla_extremo_circ 0.2 7 &
wait; echo fin
