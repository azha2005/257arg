"""Provincias y elecciones provinciales para la proyeccion con pocas mesas (ver LEEME.md de esta carpeta).

PROVINCIAS: distrito de la DINE, unidad de informe (seccion electoral o departamento), estratos para repesar las
actas y camaras con sus bancas. ELECCIONES: de donde sale cada eleccion provincial por mesa y como se leen sus columnas.
Camaras, renovacion y regla de la PBA verificadas el 29-oct-2026 (ver LEEME.md, «Verificación de las bancas»)."""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
AMBITOS = os.path.join(ROOT, "datos_oficiales", "2025", "x", "ambitosElectorales.csv")
# Los 24 partidos del conurbano (seccion_id de la DINE), los mismos de fotos_modelo.GBA
GBA = [3, 4, 11, 36, 38, 52, 53, 61, 62, 70, 77, 79, 80, 92, 105, 106, 113, 118, 122, 129, 130, 132, 133, 134]

PROVINCIAS = {
    "pba": dict(
        distrito="02", nombre="Provincia de Buenos Aires",
        unidad="seccion_electoral",          # seccionprovincial_id de ambitosElectorales.csv (8 = La Plata)
        # estrato "AMBA" = conurbano: el motor lo informa como «Peso AMBA»
        estrato=lambda d, s: np.where(np.isin(np.asarray(s).astype(int), GBA), "AMBA", "interior"),
        # Ley 5109, arts. 109-110 (detalle en proyectar_prov.hare_piso): cociente Hare por seccion sin blancos ni
        # anulados, piso en el cociente, restos a los mayores residuos y lo que sobre a la lista mas votada.
        regla="hare_piso",
        # Bancas por seccion electoral (1.a a 7.a y 8 = Capital/La Plata): Ley 5109, art. 13. La Ley 14.086 (100 y
        # 50) fue observada por el Decreto 2997/09; 2023 y 2025 se eligieron con estas.
        camaras={"senadores": {1: 8, 2: 5, 3: 9, 4: 7, 5: 5, 6: 6, 7: 3, 8: 3},
                 "diputados": {1: 15, 2: 11, 3: 18, 4: 14, 5: 11, 6: 11, 7: 6, 8: 6}},
        # Que camara elige cada seccion: 2025 segun la prensa (Chequeado, El Economista); 2027 como 2023 (Wikipedia).
        renueva={2025: {"senadores": [1, 4, 5, 7], "diputados": [2, 3, 6, 8]},
                 2027: {"senadores": [2, 3, 6, 8], "diputados": [1, 4, 5, 7]}},
    ),
}

# Nombres de partido o departamento que no coinciden con los de la DINE: {distrito: {nombre: seccion_id}}
ALIAS = {"02": {"25 DE MAYO": 121, "GENERAL MADARIAGA": 47, "PARTIDO DE LA COSTA": 119}}

# Elecciones provinciales por mesa. archivo: CSV largo, una fila por mesa y lista (UTF-8 o latin-1).
# columnas: nombre en el archivo -> nombre interno. Internos: seccion (nombre o codigo DINE del partido o
# departamento), circuito, mesa, mesa_tipo (opcional), electores (opcional), cargo (opcional), lista, tipo
# (opcional: positivo / blanco / nulo / recurrido...), votos.
# cargo: expresion regular para quedarse con un cargo (el que sigue a la eleccion nacional: diputados o senadores
# provinciales; en la PBA cada seccion vota uno solo de los dos). listas: CSV lista,bloque (columna seccion
# opcional para listas que cambian de bloque segun la seccion). filtro: {columna: valor} para quedarse con una
# eleccion de un archivo que trae varias. Sin circuito ni mesa el archivo es por partido: se usa como origen por
# seccion (las actas se comparan con su partido) y no da electores por mesa.
ELECCIONES = {
    "pba2025": dict(
        provincia="pba", fecha="2025-09-07",
        archivo=os.path.join(ROOT, "datos", "provinciales", "pba2025", "mesas.csv"),   # pedido a graficarpba
        columnas={},                       # completar cuando llegue el archivo (p. ej. {"partido": "seccion"})
        cargo=r"SENADOR|DIPUTAD",
        listas=os.path.join(ROOT, "datos", "provinciales", "pba2025", "listas.csv"),
    ),
    # Provinciales 2023 por partido, del catalogo de datos abiertos de la provincia (datos/provinciales/gba_catalogo)
    "pba2023": dict(
        provincia="pba", fecha="2023-10-22",
        archivo=os.path.join(ROOT, "datos", "provinciales", "gba_catalogo", "elecciones-generales-2005-2023.csv"),
        columnas={"distrito": "seccion", "votantes_habilitados": "electores"},
        filtro={"eleccion": "2023"}, cargo=r"SENADORES PROV|DIPUTADOS PROV",
        listas=os.path.join(ROOT, "datos", "provinciales", "pba2023", "listas.csv"),
    ),
}
