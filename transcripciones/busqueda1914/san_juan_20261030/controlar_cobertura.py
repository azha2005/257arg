"""Control de cobertura y sumas observadas; nunca transforma silencios en ceros."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ["mesas_capital.csv", "mesas_trinidad_desamparados.csv", "otras_mesas.csv", "mesas_resto_provincia.csv"]
rows = []
for name in FILES:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            row["archivo"] = name
            rows.append(row)
keys = [(r["colegio"], r["mesa"], r["fecha_eleccion"]) for r in rows]
assert len(keys) == len(set(keys)) == 114
assert sum(r["fecha_eleccion"] == "1914-04-05" for r in rows) == 2
assert all(r["pdf_paginas"] and r["Barrera"] for r in rows)
assert not any(r["fecha_eleccion"] == "1914-03-22" and
               (r["colegio"], r["mesa"]) in [("Capital - distrito 3", "4"), ("Angaco Norte", "2")]
               for r in rows)

groups = defaultdict(list)
for row in rows:
    groups[row["colegio"]].append(row)

def count(values):
    return {c: {"suma_observada": sum(int(r[c]) for r in values if r[c]),
                "mesas_con_mencion": sum(bool(r[c]) for r in values),
                "mesas_sin_mencion": sum(not r[c] for r in values)}
            for c in ["Barrera", "Quiroga", "Soldati", "blancos"]}

report = {
    "mesas": len(rows), "claves_unicas": len(set(keys)),
    "complementarias": 2, "colegios_literales": len(groups),
    "advertencia": "Cobertura de mesas completa; bloque de cinco sin identificar territorialmente; conciliacion provincial abierta; silencios no son ceros",
    "totales_observados": count(rows),
    "resumen_provincial_pdf69": {"Barrera": 10194, "Quiroga": 3187, "Soldati": 202, "blancos": 155, "dispersos": 17},
    "por_colegio": {name: {"mesas": len(values), **count(values)} for name, values in groups.items()},
}
report["diferencia_observado_menos_resumen"] = {
    c: report["totales_observados"][c]["suma_observada"] - report["resumen_provincial_pdf69"][c]
    for c in ["Barrera", "Quiroga", "Soldati", "blancos"]
}
(ROOT / "control_provincial.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
# Mantener compatible el archivo anterior, ahora con las 114 mesas.
legacy = {name: {"mesas": len(values), **{c: sum(int(r[c]) for r in values if r[c]) for c in ["Barrera", "Quiroga"]}} for name, values in groups.items()}
(ROOT / "cobertura_acumulada.json").write_text(json.dumps(legacy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "control_trinidad_desamparados.json").write_text(json.dumps({k: report["por_colegio"][k] for k in ["Trinidad", "Desamparados"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "por_colegio"}, ensure_ascii=False, indent=2))
for name, values in groups.items():
    print(name, len(values), {c: sum(int(r[c]) for r in values if r[c]) for c in ["Barrera", "Quiroga"]})
