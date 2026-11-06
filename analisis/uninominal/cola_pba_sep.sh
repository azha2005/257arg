# gerrymanders LLA de Buenos Aires guiados por las provinciales del 7-sep-2025 (local: base de graficarpba)
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
(UNI_GUIA=pba25s UNI_PLAN=plan_gpba25s UNI_INICIO=plan_radios_lla_circ "$PY" distritar.py 02 --modo lla --circuitos --tol 0.02 --iter 30000 --workers 1 > plan_gpba25s_lla_log.txt 2>&1) &
(UNI_GUIA=pba25s UNI_PLAN=plan_gpba25s UNI_INICIO=plan_radios_lla_extremo_circ UNI_SWING=0.05 "$PY" distritar.py 02 --modo lla_extremo --circuitos --tol 0.02 --iter 30000 --workers 1 > plan_gpba25s_lla_extremo_log.txt 2>&1) &
wait; echo fin
