# LLA extremo de Buenos Aires con las provinciales del 7-sep-2025, margenes finos (UNI_SIG 0,01 y 0,005)
PY="/c/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe"
for s in 010 005; do
(UNI_GUIA=pba25s UNI_SIG=0.$s UNI_PLAN=plan_gpba25s_fino$s UNI_INICIO=plan_gpba25s_lla_extremo_circ "$PY" distritar.py 02 --modo lla_extremo --circuitos --tol 0.02 --iter 100000 --workers 1 > plan_gpba25s_fino${s}_log.txt 2>&1) &
done
wait; echo fin
