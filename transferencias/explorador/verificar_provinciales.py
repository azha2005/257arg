"""Comprueba todos los empalmes provinciales y sus accesos desde el catálogo nacional.

    python -X utf8 transferencias/explorador/verificar_provinciales.py
    python -X utf8 transferencias/explorador/verificar_provinciales.py --solo-alineacion

Cada par se prueba en ambos sentidos, con la nacional preparada y con la curada.
El cálculo completo verifica ambos modos (validación cruzada y rápido).
"""
import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(variable, "1")

import json
from pathlib import Path
import sys
import time
import numpy as np
import datos
import motor


def verificar():
    inicio = time.time()
    resultados, errores = [], []
    solo = "--solo-alineacion" in sys.argv
    for f in datos.PROVPKL:
        for k, (X, Y, meta) in datos._bases(f).items():
            o, d = "pr:%s|%s|o" % (f, k), "pr:%s|%s|d" % (f, k)
            lp = "d" if datos.nacional_preparada(meta["origen"]) else "o"
            ln = "o" if lp == "d" else "d"
            provincial = "pr:%s|%s|%s" % (f, k, lp)
            nacional = datos.nacional_preparada(meta["origen" if ln == "o" else "destino"])
            assert nacional, (f, k, meta)
            alias = (nacional, provincial) if ln == "o" else (provincial, nacional)
            pares = [(o, d), (d, o), alias, alias[::-1]]
            for a, b in pares:
                registro = dict(origen=a, destino=b)
                try:
                    A, B, info, notas, nivel = motor.alinear(a, b)
                    assert A.index.equals(B.index)
                    assert A.index.is_unique and len(A) >= 3
                    assert len(A) == len(X) == len(Y), (len(A), len(X), len(Y))
                    # El acceso curado conserva exactamente el empalme preparado,
                    # incluida su cobertura: no reintroduce unidades excluidas.
                    for eid, T in ((a, A), (b, B)):
                        esperado = datos.tabla(eid if eid.startswith("pr:") else "pr:%s|%s|%s" % (f, k, ln))
                        assert T.equals(esperado), "El empalme cambió los votos o las unidades de la fuente."
                    registro.update(unidades=len(A), nivel=nivel)
                    registro["calculos"] = []
                    if not solo:
                        for rapido in (False, True):
                            R = motor.calcular(a, b, rapido=rapido)
                            M = np.asarray(R["nacional"])
                            assert M.shape == (len(R["rows"]), len(R["cols"]))
                            assert np.isfinite(M).all() and (M >= 0).all()
                            AA, BB, _ = motor._base_comun(A, B, [])
                            AA, BB = AA.fillna(0), BB.fillna(0)
                            assert R["unidades"] == len(AA), (R["unidades"], len(AA))
                            provs = np.sum([np.asarray(p) for p in R["provincias"].values()], axis=0)
                            np.testing.assert_allclose(M, provs, atol=.11)
                            assert abs(M.sum() - BB.sum().sum()) <= M.size * .051
                            assert len(R["notas"]) >= 3
                            if "Blanco" in A or "Blanco" in B:
                                assert R["base"] == "votos válidos (positivos + blancos)"
                                assert "Blanco" in R["rows"] + R["cols"]
                            registro["calculos"].append(dict(rapido=rapido, unidades=R["unidades"], segundos=R["segundos"]))
                except Exception as e:
                    registro["error"] = "%s: %s" % (type(e).__name__, e)
                    errores.append(registro)
                    print("  ERROR %s -> %s: %s" % (a, b, registro["error"]), flush=True)
                resultados.append(registro)
            print("%s/%s: %d unidades; %d errores acumulados" % (f, k, len(X), len(errores)), flush=True)
    reporte = dict(version=motor.VERSION, empalmes=sum(len(datos._bases(f)) for f in datos.PROVPKL),
                   accesos=len(resultados), calculos=sum(len(r.get("calculos", [])) for r in resultados),
                   errores=errores, segundos=round(time.time() - inicio, 1), resultados=resultados)
    destino = Path(__file__).with_name("VALIDACION_PROVINCIALES.json")
    destino.write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({k: v for k, v in reporte.items() if k != "resultados"}, ensure_ascii=False, indent=2))
    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    verificar()
