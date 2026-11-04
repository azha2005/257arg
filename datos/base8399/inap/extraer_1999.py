#!/usr/bin/env python3
"""Pasa a CSV los porcentajes por departamento de 1999 de la base del INAP (Reforma Politica, «Datos Departamentales 1999»).

    python datos/base8399/inap/extraer_1999.py [carpeta]      (por defecto andytow/, en la raiz del proyecto)

Escribe 1999_<cargo>_pct.csv (provincia, departamento, sigla, partido, codigo, pct). Es el escrutinio provisorio de INDRA
y trae solo porcentajes sobre votos positivos, sin votos ni totales: ver LEEME.md.
"""
import csv, os, sys
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "andytow")
FILES = {"presidente": "1999 Presidente.xls", "diputados": "1999 diputados nacionales.xls",
         "gobernador": "1999 Gobernador.xls", "diputados_prov": "1999 Diputados Provinciales.xls"}

for cargo, fn in FILES.items():
    s = xlrd.open_workbook(os.path.join(SRC, fn), ignore_workbook_corruption=True).sheet_by_index(0)
    h = s.row_values(0)
    col = lambda v, c: v[h.index(c)] if c in h else ""
    out = os.path.join(HERE, "1999_%s_pct.csv" % cargo)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["provincia", "departamento", "sigla", "partido", "codigo", "pct"])
        for r in range(1, s.nrows):
            v = s.row_values(r)
            w.writerow([col(v, "proNombre"), col(v, "depNombre"), col(v, "parSiglas"), col(v, "parDenominacion"), col(v, "parCodigo"), col(v, "votPorcenVotos")])
    print(out, s.nrows - 1, "filas")
