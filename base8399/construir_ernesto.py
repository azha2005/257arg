#!/usr/bin/env python3
"""Capa 3 de base8399: bases de Ernesto Calvo (carpeta «Bases Ernesto/País x Departamento», TPDENP19xxT.xls).

    python construir_ernesto.py "<carpeta Bases Ernesto>"   ->  base8399/ernesto/

Salidas
  ernesto/AAAA_<cargo>/dpto_partidos.csv   votos por departamento y columna de partido, formato largo
  ernesto/codigos_AAAA.csv                 leyendas de la hoja «Códigos» de cada archivo (texto sin interpretar)
  ernesto/anomalias.csv                    columnas cuyo sufijo de año no coincide con el del archivo o de categoría desconocida
  ernesto/resumen.csv                      filas, provincias y departamentos por año y cargo

No se corrige ni imputa nada. Celda vacía = sin dato (no cero). Las columnas que son positivos (`pos`, suma de las agrupaciones), nulos, blancos o totales
se marcan en `tipo_fila` y no deben sumarse con las agrupaciones; `electores` es el padrón de la unidad: cuando la hoja trae una sola columna `electores` se replica en todos los cargos de esa hoja; si trae varias, se asigna al cargo del bloque anterior (inferencia de posición).
Requiere xlrd (pip install xlrd).
"""
import sys, os, re, csv, glob, collections
import xlrd

CARGO = {"p": "presidente", "dn": "diputados", "sn": "senadores_nac", "g": "gobernador", "dp": "diputados_prov", "sp": "senadores_prov"}
RE_COL = re.compile(r"^(?P<code>.+?)(?P<yy>\d\d)(?P<cat>[a-z]+)$")
CAT_OTRAS = {"c", "cn", "cc", "cp", "dd", "ddu", "lp", "lc", "fn", "pdn", "lpd", "lpr", "dpd"}
PROVS = ["Buenos Aires", "Capital Federal", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa",
         "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe", "Santiago del Estero",
         "Tierra del Fuego", "Tucumán"]
RE_ELEC = re.compile(r"^electores(?:\d{2,4})?(?:[a-z]+)?(?:\(\d\))?$")


def unacc(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("�", "").strip()


CANON = {unacc(p): p for p in PROVS}


def es_hoja_aux(nombre):
    n = unacc(nombre)
    return n.startswith(("cod", "criterios", "categor", "observ")) or "codific" in n


def tipo_fila(code):
    c = code.lower()
    if c == "pos": return "positivos"
    if c.startswith(("nul", "nulo")): return "nulos"
    if c.startswith(("bla", "blanco")): return "blancos"
    if c.startswith(("imp", "recur", "rec")): return "impugnados_recurridos"
    if c in ("tot", "total", "totales") or c.startswith("tot"): return "total"
    return "agrupacion"


def num(c):
    if c.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK): return ""
    v = c.value
    if isinstance(v, str):
        v = v.strip()
        if not v: return ""
        try: v = float(v.replace(",", "."))
        except ValueError: return None
    return int(round(v)) if abs(v - round(v)) < 1e-9 else v


def main(src):
    base = os.path.join(src, "País x Departamento")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ernesto")
    os.makedirs(out, exist_ok=True)
    rows_by = collections.defaultdict(list)
    anomal, resumen = [], collections.defaultdict(lambda: [0, set(), set()])
    for path in sorted(glob.glob(os.path.join(base, "TPDENP*T.xls"))):
        fy = int(re.search(r"TPDENP(\d{4})T", path).group(1))
        wb = xlrd.open_workbook(path)
        with open(os.path.join(out, "codigos_%d.csv" % fy), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f); w.writerow(["hoja", "fila", "c1", "c2", "c3", "c4"])
            for sh in wb.sheets():
                if es_hoja_aux(sh.name):
                    for r in range(sh.nrows):
                        vals = [str(sh.cell_value(r, k)).strip() for k in range(min(sh.ncols, 4))]
                        if any(vals): w.writerow([sh.name, r + 1] + vals + [""] * (4 - len(vals)))
        for sh in wb.sheets():
            if es_hoja_aux(sh.name) or sh.nrows < 2: continue
            hdr = [str(c.value).strip() for c in sh.row(0)]
            hl = [h.lower() for h in hdr]
            kd = next((k for k, h in enumerate(hl[:3]) if h.startswith("depart")), 1)
            ki = next((k for k, h in enumerate(hl[:4]) if h.startswith("indra")), kd + 1)
            kp = next((k for k, h in enumerate(hl[:3]) if h.startswith(("provincia", "distrito"))), None)
            first = max(kd, ki, kp if kp is not None else 0) + 1
            pcanon = CANON.get(unacc(sh.name))
            if pcanon is None:
                anomal.append([fy, sh.name, "", "hoja con nombre de provincia no reconocido; se omite"]); continue
            cols, last = [], None
            n_elec = sum(1 for h in hdr[first:] if RE_ELEC.match(h.lower()))
            for k, h in enumerate(hdr):
                if k < first or not h: continue
                if RE_ELEC.match(h.lower()) and last:
                    cols.append((k, "electores", last if n_elec > 1 else "*", True)); continue
                m = RE_COL.match(h.lower())
                if not m:
                    anomal.append([fy, sh.name, h, "nombre sin sufijo año+categoría"]); continue
                cat, yy = m.group("cat"), int(m.group("yy"))
                yyyy = 1900 + yy if yy >= 30 else 2000 + yy
                if cat not in CARGO and cat not in CAT_OTRAS:
                    anomal.append([fy, sh.name, h, "categoría desconocida"]); continue
                if yyyy != fy:
                    anomal.append([fy, sh.name, h, "año de la columna (%d) distinto del archivo" % yyyy]); continue
                cols.append((k, m.group("code"), cat, False)); last = cat
            for r in range(1, sh.nrows):
                dpto = sh.cell_value(r, kd)
                if isinstance(dpto, float) and dpto == int(dpto): dpto = str(int(dpto))
                dpto = str(dpto).strip()
                if not dpto: continue
                indra = sh.cell_value(r, ki)
                if isinstance(indra, float): indra = "%05d" % int(indra)
                indra = str(indra).strip()
                prov = pcanon
                for k, code, cat, es_el in cols:
                    v = num(sh.cell(r, k))
                    if v == "": continue
                    if v is None:
                        anomal.append([fy, sh.name, "%s fila %d" % (hdr[k], r + 1), "valor no numérico: %r" % sh.cell_value(r, k)]); continue
                    if cat == "*":      # un solo padron por hoja: se replica en cada cargo de la hoja
                        for cat2 in sorted({c[2] for c in cols if c[2] != "*"}):
                            cg = CARGO.get(cat2, "otras_" + cat2)
                            rows_by[(fy, cg)].append([prov, fy, cg, dpto, indra, hdr[k], code, "electores", v, os.path.basename(path), sh.name.strip()])
                            s = resumen[(fy, cg)]; s[0] += 1; s[1].add(prov); s[2].add((prov, dpto))
                        continue
                    cargo = CARGO.get(cat, "otras_" + cat)
                    rows_by[(fy, cargo)].append([prov, fy, cargo, dpto, indra, hdr[k], code, "electores" if es_el else tipo_fila(code), v, os.path.basename(path), sh.name.strip()])
                    s = resumen[(fy, cargo)]; s[0] += 1; s[1].add(prov); s[2].add((prov, dpto))
    head = ["provincia", "anio", "cargo", "departamento", "codigo_indra", "columna_fuente", "codigo_partido", "tipo_fila", "votos", "archivo", "hoja"]
    for (fy, cargo), rows in sorted(rows_by.items()):
        d = os.path.join(out, "%d_%s" % (fy, cargo)); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "dpto_partidos.csv"), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f); w.writerow(head); w.writerows(rows)
    with open(os.path.join(out, "anomalias.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["archivo_anio", "hoja", "columna", "motivo"]); w.writerows(anomal)
    with open(os.path.join(out, "resumen.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["anio", "cargo", "filas", "provincias", "unidades"])
        for (fy, cargo), (n, p, u) in sorted(resumen.items()): w.writerow([fy, cargo, n, len(p), len(u)])
    print("escrito", out, "| elecciones/cargos:", len(rows_by), "| anomalías:", len(anomal))


if __name__ == "__main__":
    main(sys.argv[1])
