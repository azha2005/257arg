# LLA extremo PBA 7-sep-2025, margen de un punto, busqueda mas caliente y con otras semillas/arranques
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
c() { UNI_GUIA=pba25s UNI_SIG=0.01 UNI_TEMP=$3 UNI_PLAN=plan_gpba25s_$1 UNI_INICIO=$2 "$PY" distritar.py 02 --modo lla_extremo --circuitos --tol 0.02 --iter 300000 --seed $4 --workers 1 > plan_gpba25s_$1_log.txt 2>&1; }
c t1 plan_gpba25s_fino010_lla_extremo_circ 0.01 2 &
c t2 plan_gpba25s_fino010_lla_extremo_circ 0.03 3 &
c t3 plan_radios_lla_extremo_circ 0.01 4 &
wait; echo fin
