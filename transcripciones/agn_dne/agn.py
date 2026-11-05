"""Transcripciones propias de planillas del Archivo General de la Nación, fondo Dirección Nacional Electoral (AR-AGN-DNE01).

Devuelve «páginas» con el mismo formato que las de Cantón (transcripciones/canton5865/transcripcion/p_*.json), para que
canton5865/cargar.py las sume a sus tablas. Cada CSV es una planilla; la fila «TOTAL GENERAL» es el control y no se carga.
"""
import csv, os

H = os.path.dirname(os.path.abspath(__file__))

PLANILLAS = [   # (csv, año, elección, provincia, cita)
    ("sde1962/sde1962.csv", 1962, "Diputados", "Santiago del Estero",
     "AGN, DNE01, Resultados, carpeta AR-AGN-DNE01-De-re-29_056_246a273, f. 247-251"),
]
NO_VOTO = {"hoja", "folio", "departamento"}
RENOMBRE = {"Electores hábiles": "Inscriptos (electores hábiles)",
            "Autonomista": "Autonomista de Santiago del Estero",
            "UCRI": "Unión Cívica Radical Intransigente",
            "UCR de Santiago del Estero": "Unión Cívica Radical de Santiago del Estero"}


def paginas():
    out = []
    for fn, anio, elec, prov, cita in PLANILLAS:
        rows = list(csv.DictReader(open(os.path.join(H, fn), encoding="utf-8")))
        names = [c for c in rows[0] if c not in NO_VOTO]
        cols = {str(i + 1): RENOMBRE.get(c, c) for i, c in enumerate(names)}
        filas = [dict(departamento=r["departamento"], valores={str(i + 1): int(r[c]) for i, c in enumerate(names)})
                 for r in rows if r["departamento"] != "TOTAL GENERAL"]
        out.append(dict(pagina_pdf=cita, anio=anio, eleccion=elec, provincia=prov, categoria="varones y mujeres",
                        columnas=cols, filas=filas, fuente="AGN", _file=fn))
    return out


def control():
    """Cada fila cierra (partidos + blancos + anulados = votantes) y cada columna da el total general de la planilla."""
    for fn, *_ in PLANILLAS:
        rows = list(csv.DictReader(open(os.path.join(H, fn), encoding="utf-8")))
        names = [c for c in rows[0] if c not in NO_VOTO]
        tot = next(r for r in rows if r["departamento"] == "TOTAL GENERAL")
        dep = [r for r in rows if r is not tot]
        for r in dep:
            s = sum(int(r[c]) for c in names if c not in ("Votantes", "Electores hábiles"))
            print(fn, r["departamento"], "OK" if s == int(r["Votantes"]) else "suma %d != votantes %s" % (s, r["Votantes"]))
        for c in names:
            s = sum(int(r[c]) for r in dep)
            if s != int(tot[c]): print(fn, "columna", c, ": suma de departamentos", s, "contra total de la planilla", tot[c])


if __name__ == "__main__":
    control()
