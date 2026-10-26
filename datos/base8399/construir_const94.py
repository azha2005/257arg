"""Convencionales constituyentes de 1994 por departamento, de la base de Ernesto Calvo.

    python construir_const94.py "<carpeta Bases Ernesto>"     -> ernesto/1994_constituyentes/dpto_partidos.csv (+ anomalias.csv)

Origen: «Bases Ernesto/País x Departamento/1994-const.xls» (hojas: const_94 = resumen de Capital, observaciones, Codigos y una hoja por provincia).
Mismo formato largo que `ernesto/<AÑO>_<cargo>/dpto_partidos.csv` (ver ernesto/LEEME.md). Se usan solo las columnas «..94cn» (convencionales nacionales);
las «..94cp» de algunas provincias son otra cosa (se dejan afuera).
Las hojas no son homogéneas, y el script lo resuelve asi (cada caso queda en anomalias.csv):
  - Chaco trae dos columnas «pos94cn»: la primera son los positivos y la segunda los blancos.
  - La Rioja trae «ucr94dn» y «pos94dn» (letra equivocada): se leen como cn.
  - Mendoza llama «vot94cn» al total y Neuquen «totales».
  - Santa Cruz llama «pj0094cn» y «ucr0094cn» a pj y ucr (el «00» es la lista).
  - Tierra del Fuego trae una fila «sector antartico argentino» sin codigo INDRA.
  - Capital Federal trae una fila por circunscripcion (1 a 28).
"""
import os, re, sys, csv
import xlrd

SRC = os.path.join(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "../Bases Ernesto"), "País x Departamento", "1994-const.xls")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ernesto", "1994_constituyentes")
os.makedirs(OUT, exist_ok=True)
PROV = {"capital federal": "Capital Federal", "cordoba": "Córdoba", "neuquen": "Neuquén", "rio negro": "Río Negro", "tucuman": "Tucumán", "entre ríos": "Entre Ríos"}
TIPO = {"pos": "positivos", "bla": "blancos", "nul": "nulos", "tot": "total", "vot": "total", "totales": "total", "rec": "impugnados_recurridos", "imp": "impugnados_recurridos", "impug": "impugnados_recurridos"}

wb = xlrd.open_workbook(SRC)
rows, anom = [], []
for name in wb.sheet_names()[3:]:
    sh = wb.sheet_by_name(name)
    hdr = [str(sh.cell_value(0, c)).strip().lower() for c in range(sh.ncols)]
    prov = PROV.get(name.strip().lower(), name.strip())
    # columnas
    cols = []   # (indice, tipo_fila, codigo_partido, nombre de la columna)
    seen_pos = 0
    for c, h in enumerate(hdr):
        m = re.fullmatch(r"([a-z]+?)(?:00|01|02)?(94)(c[np]|dn)", h)
        if not m:
            if h == "totales": cols.append((c, "total", "", h))
            continue
        base, suf = m.group(1), m.group(3)
        if suf == "cp": continue
        if suf == "dn":
            anom.append((prov, h, "sufijo dn en una hoja de convencionales: se lee como cn"))
        if base == "pos":
            seen_pos += 1
            if name.strip().lower() == "chaco" and seen_pos == 2:
                cols.append((c, "blancos", "", h)); anom.append((prov, h, "segunda columna pos94cn de Chaco: son los blancos")); continue
            cols.append((c, "positivos", "", h)); continue
        if base in TIPO:
            cols.append((c, TIPO[base], "", h)); continue
        code = base
        cols.append((c, "agrupacion", code, h))
        if re.search(r"(00|01|02)94", h): anom.append((prov, h, "lista numerada (%s): se suma bajo el codigo %s" % (h, code)))
    ci = hdr.index("electores") if "electores" in hdr else None
    for r in range(1, sh.nrows):
        row = [sh.cell_value(r, c) for c in range(sh.ncols)]
        dep = row[1]
        if prov == "Capital Federal":
            dep = str(int(dep))
        else:
            dep = str(dep).strip()
        if not dep: continue
        indra = row[2]
        indra = ("%05d" % int(indra)) if isinstance(indra, float) else str(indra).strip()
        if name.strip().lower() == "tierra del fuego" and "antartico" in dep.lower():
            anom.append((prov, dep, "fila sin codigo INDRA: Sector Antartico Argentino (se suma luego a Ushuaia en el atlas)"))
        for c, tipo, code, h in cols:
            v = row[c]
            if v == "" or v is None: continue
            if isinstance(v, str):
                anom.append((prov, "%s/%s" % (dep, h), "celda de texto %r" % v)); continue
            rows.append((prov, dep, indra, h, code, tipo, v))
        if ci is not None and row[ci] != "" and not isinstance(row[ci], str):
            rows.append((prov, dep, indra, "electores", "", "electores", row[ci]))
with open(os.path.join(OUT, "dpto_partidos.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["provincia", "anio", "cargo", "departamento", "codigo_indra", "columna_fuente", "codigo_partido", "tipo_fila", "votos", "archivo", "hoja"])
    for prov, dep, indra, h, code, tipo, v in rows:
        w.writerow([prov, 1994, "constituyentes", dep, indra, h, code, tipo, int(v) if v == int(v) else v, "1994-const.xls", prov])
with open(os.path.join(OUT, "anomalias.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["provincia", "dato", "nota"]); w.writerows(anom)
print("filas", len(rows), "| unidades", len({(r[0], r[1]) for r in rows}), "| anomalias", len(anom))
