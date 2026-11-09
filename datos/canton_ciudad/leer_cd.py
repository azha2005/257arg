"""Lee las 106 planillas del CD de Canton y Jorrat, *Elecciones en la ciudad*
(tomo III, 2007) y las pasa a un CSV largo.

Uso:  python datos/canton_ciudad/leer_cd.py
Salida: datos/canton_ciudad/cd_largo.csv, cd_elecciones.json y cd_control.json

No corrige ni imputa nada: copia lo que dice cada hoja. Los controles
(suma de unidades contra la fila TOTAL, votos contra votantes) van a
cd_control.json para revisarlos a mano.
"""
import csv
import glob
import json
import os
import re
import sys

import xlrd

AQUI = os.path.dirname(os.path.abspath(__file__))
CD = os.path.join(AQUI, "cd")

CLAVES_HDR = ("INSCRIP", "CIRCUNSC", "PARROQ", "SECCI")


def limpio(x):
    if isinstance(x, float):
        return x
    return re.sub(r"\s+", " ", str(x)).strip()


def num(x):
    if isinstance(x, float):
        return x
    s = limpio(x).replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def fila_encabezado(s):
    for r in range(min(s.nrows, 20)):
        v = [str(x).upper() for x in s.row_values(r)]
        txt = " ".join(v)
        llenas = sum(1 for x in v if x.strip())
        if llenas >= 3 and any(k in txt for k in CLAVES_HDR):
            return r
    return None


def leer_hoja(s):
    hr = fila_encabezado(s)
    titulo = [limpio(s.cell_value(r, 1)) for r in range(0, hr if hr is not None else min(6, s.nrows))
              if s.ncols > 1 and limpio(s.cell_value(r, 1)) != ""]
    if hr is None:
        notas = [limpio(c) for r in range(s.nrows) for c in s.row_values(r)
                 if isinstance(c, str) and len(c.strip()) > 3]
        return {"titulo": titulo, "columnas": [], "unidades": [], "total": None, "notas": notas}
    hdr = [limpio(x) for x in s.row_values(hr)]
    # columna del nombre de la unidad: la del encabezado CIRCUNSC/PARROQ/SECCI
    c_nom = next((i for i, h in enumerate(hdr) if any(k in str(h).upper() for k in ("CIRCUNSC", "PARROQ", "SECCI"))), None)
    if c_nom is None:  # sin rótulo: la columna anterior a INSCRIPTOS
        c_nom = next(i for i, h in enumerate(hdr) if "INSCRIP" in str(h).upper()) - 1
    cols = [(i, h) for i, h in enumerate(hdr) if i > c_nom and h != ""]
    unidades, total, notas = [], None, []
    for r in range(hr + 1, s.nrows):
        fila = s.row_values(r)
        nombre = limpio(fila[c_nom]) if c_nom < len(fila) else ""
        numero = fila[c_nom - 1] if c_nom >= 1 else ""
        valores = {h: num(fila[i]) if i < len(fila) else None for i, h in cols}
        hay = sum(1 for v in valores.values() if v is not None)
        es_total = any(str(c).strip().upper().startswith(("TOTAL", "SUMA")) for c in fila[:c_nom + 1])
        if es_total and total is not None:  # segunda fila de totales: no pisar la primera
            continue
        if es_total:
            total = valores
            continue
        if hay >= 1 and (nombre or nombre == 0) and nombre != "" and not str(nombre).upper().startswith(("FUENTE", "NOTA")):
            if isinstance(nombre, float):  # 1951: la columna del nombre trae el número
                numero, nombre = nombre, ""
            unidades.append({
                "numero": int(numero) if isinstance(numero, float) else (limpio(numero) or None),
                "nombre": nombre,
                "valores": valores,
                "crudo": {h: (fila[i] if i < len(fila) else "") for i, h in cols},
            })
            continue
        for c in fila:
            if isinstance(c, str) and len(c.strip()) > 3:
                notas.append(limpio(c))
    return {"titulo": titulo, "columnas": [h for _, h in cols], "unidades": unidades,
            "total": total, "notas": notas}


def main():
    archivos = sorted(glob.glob(os.path.join(CD, "*")),
                      key=lambda f: int(re.search(r"\((\d+)\)", f).group(1)))
    filas, elecciones, control = [], [], []
    for f in archivos:
        base = os.path.basename(f)
        n = int(re.search(r"\((\d+)\)", base).group(1))
        cod = re.search(r"CF(\d{4})([A-Za-z0-9]+)\.", base)
        anio, tipo = int(cod.group(1)), cod.group(2).upper()
        wb = xlrd.open_workbook(f, ignore_workbook_corruption=True)
        hojas = []
        for s in wb.sheets():
            h = leer_hoja(s)
            nom = s.name.strip().upper()
            sexo = "V" if nom.startswith("VAR") else "M" if nom.startswith("MUJ") else ("AS" if tipo.endswith("AS") else "V")
            hojas.append(sexo)
            for u in h["unidades"]:
                for col, v in u["valores"].items():
                    filas.append({"n": n, "archivo": base, "anio": anio, "tipo": tipo, "sexo": sexo,
                                  "unidad_num": u["numero"], "unidad": u["nombre"], "columna": col,
                                  "valor": "" if v is None else (int(v) if float(v).is_integer() else v),
                                  "crudo": "" if v is not None else limpio(u["crudo"][col])})
            # controles
            if h["unidades"]:
                for col in h["columnas"]:
                    vs = [u["valores"][col] for u in h["unidades"] if u["valores"].get(col) is not None]
                    suma = sum(vs)
                    tot = (h["total"] or {}).get(col)
                    if tot is not None and abs(suma - tot) > 0.5:
                        control.append({"n": n, "archivo": base, "sexo": sexo, "tipo": "suma != TOTAL",
                                         "columna": col, "suma_unidades": suma, "total_hoja": tot,
                                         "diferencia": suma - tot})
            elecciones.append({"n": n, "archivo": base, "anio": anio, "tipo": tipo, "sexo": sexo,
                               "hoja": s.name, "titulo": h["titulo"], "columnas": h["columnas"],
                               "unidades": len(h["unidades"]), "total": h["total"], "notas": h["notas"]})
    with open(os.path.join(AQUI, "cd_largo.csv"), "w", newline="", encoding="utf-8-sig") as fo:
        w = csv.DictWriter(fo, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    with open(os.path.join(AQUI, "cd_elecciones.json"), "w", encoding="utf-8") as fo:
        json.dump(elecciones, fo, ensure_ascii=False, indent=1)
    with open(os.path.join(AQUI, "cd_control.json"), "w", encoding="utf-8") as fo:
        json.dump(control, fo, ensure_ascii=False, indent=1)
    print(len(archivos), "archivos,", len(elecciones), "hojas,", len(filas), "celdas,", len(control), "avisos de cierre")


if __name__ == "__main__":
    sys.exit(main())
