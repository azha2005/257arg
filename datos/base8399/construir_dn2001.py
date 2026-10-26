#!/usr/bin/env python3
"""Diputados nacionales 2001 por departamento, de Bases Ernesto/2001 x DTO/Diputados Nacionales/*.xls (una planilla por provincia).

    python construir_dn2001.py "<carpeta Bases Ernesto>"   ->  ernesto/2001_diputados/dpto_partidos.csv + mapeo_columnas.csv + control.csv

Las planillas traen solo el codigo de departamento (PROV_I_1, DTO = codigo INDRA) y una columna por lista o partido (en Cordoba, una por cada partido de
la lista conjunta). Los nombres salen de las bases de Ernesto de otros anos por el mismo codigo INDRA (1997, 1995, 1993, 1999: en ese orden, porque los codigos de 1999 tienen algun nombre cambiado, p. ej. Escobar).
`agrupaciones/DN01.xls`, hoja `dn2001`, trae para cada columna de cada provincia el nombre de la lista y el grupo («group») que le asigno Ernesto; se
copia a `mapeo_columnas.csv`.

Formato largo igual al de las otras elecciones (ver ernesto/LEEME.md): tipo_fila = agrupacion | positivos | blancos | nulos | impugnados_recurridos | total | electores.
"""
import sys, os, re, csv, glob, collections
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "../Bases Ernesto")
OUT = os.path.join(HERE, "ernesto", "2001_diputados")
os.makedirs(OUT, exist_ok=True)

# nombres: codigo INDRA -> (provincia, departamento). La numeracion de los departamentos cambia entre anos en algunas provincias: por cada una se eligio el ano
# cuya numeracion mejor reproduce el orden de votos de 2001 (correlacion de Spearman por provincia, ver control_nombres.csv): San Luis 1993 (1995: -0,25) y Santiago del Estero 1995 (1997: 0,74).
ORDEN = (1997, 1995, 1993, 1999, 1991, 1989)
PREF = {"19": 1993, "22": 1995}
NAMES = {}   # (ano, codigo) -> (provincia, departamento)
for yr in ORDEN:
    fn = os.path.join(HERE, "ernesto", "%d_diputados" % yr, "dpto_partidos.csv")
    if not os.path.exists(fn): continue
    for r in csv.DictReader(open(fn, encoding="utf-8-sig")):
        NAMES.setdefault((yr, r["codigo_indra"]), (r["provincia"], r["departamento"], yr))


def nombre(code):
    for yr in ([PREF[code[:2]]] if code[:2] in PREF else []) + list(ORDEN):
        if (yr, code) in NAMES: return NAMES[(yr, code)]
    return None


SPECIAL = {"POS": "positivos", "BLAN": "blancos", "NUL": "nulos", "REC": "impugnados_recurridos", "IMP": "impugnados_recurridos", "ELEC": "electores", "ELECT": "electores", "VOT": "total"}

rows, control, unknown = [], [], []
for f in sorted(glob.glob(os.path.join(SRC, "2001 x DTO", "Diputados Nacionales", "*.xls"))):
    sh = xlrd.open_workbook(f).sheet_by_index(0)
    hdr = [str(c.value) for c in sh.row(0)]
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        prov, dto = int(float(v[0])), int(float(v[1]))   # la primera columna es el codigo de provincia (PROV_I_1, PROV_IND, PROVINDR...)
        code = "%02d%03d" % (prov, dto)
        nm = nombre(code)
        if nm is None:
            unknown.append((os.path.basename(f), code)); nm = ("?", code, 0)
        for j, h in enumerate(hdr):
            if j < 2 or v[j] in ("", None) or not isinstance(v[j], float): continue
            m = re.match(r"^(POS|BLAN|NUL|REC|IMP|ELECT|ELEC|VOT)(_1)?$", h)
            kind = SPECIAL[m.group(1)] if m else "agrupacion"
            rows.append([nm[0], 2001, "diputados", nm[1], code, h, h, kind, int(v[j]), os.path.basename(f), os.path.basename(f)])

with open(os.path.join(OUT, "dpto_partidos.csv"), "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.writer(fo)
    w.writerow(["provincia", "anio", "cargo", "departamento", "codigo_indra", "columna_fuente", "codigo_partido", "tipo_fila", "votos", "archivo", "hoja"])
    w.writerows(rows)

# mapeo columna -> lista y grupo de Ernesto (hoja dn2001 de DN01.xls)
sh = xlrd.open_workbook(os.path.join(SRC, "agrupaciones", "DN01.xls")).sheet_by_name("dn2001")
prov_by_name = {}
with open(os.path.join(OUT, "mapeo_columnas.csv"), "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.writer(fo)
    w.writerow(["provincia_ernesto", "id", "nombre", "sigla", "columna", "grupo_ernesto", "tendencia"])
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        w.writerow([v[0], int(v[1]) if v[1] != "" else "", v[2], v[3], v[4], v[5], v[6]])
print("filas", len(rows), "| codigos sin nombre:", unknown)
