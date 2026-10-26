"""Cantón 1954 (diputados; vicepresidente o delegados en los territorios) y 1958 (presidente) o 1965 (diputados) por
departamento, en el formato de agregar_circuitos.py -> transferencias/circ_1954p.pkl y circ_1958p.pkl, o circ_1954d.pkl y
circ_1965d.pkl (sufijo d: el 1954 armado con las unidades de 1965).
    python transferencias/canton_1954_1958.py [1958|1965]
    RATIO=0.6,2.3 python transferencias/estimar.py 1954p 1958p       (o 1954d 1965d)
1954: canton1954/canton_1954.csv (tabla «varones y mujeres»). 1958: canton5865 (Cantón corregido, como el atlas).
La unidad es el departamento (circuito = nombre de 1958); seccion_id = 0. Detalle de decisiones en LEEME.md."""
import os, sys, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "canton5865"))

COD = {"Capital Federal": "01", "Buenos Aires": "02", "Catamarca": "03", "Córdoba": "04", "Corrientes": "05", "Chaco": "06",
       "Chubut": "07", "Entre Ríos": "08", "Formosa": "09", "Jujuy": "10", "La Pampa": "11", "La Rioja": "12", "Mendoza": "13",
       "Misiones": "14", "Neuquén": "15", "Río Negro": "16", "Salta": "17", "San Juan": "18", "San Luis": "19", "Santa Cruz": "20",
       "Santa Fe": "21", "Santiago del Estero": "22", "Tucumán": "23"}
# 1958 -> unidad de 1954 que la contenía (marcadas ** en Cantón 1954: «subsumidas bajo una unidad mayor»).
# Inferido de la geografía y confirmado con el padrón: cada grupo deja el crecimiento 1954-58 cerca de la mediana provincial.
GRUPO = {("Buenos Aires", "Lanús"): "Avellaneda", ("Buenos Aires", "Berisso"): "La Plata", ("Buenos Aires", "Ensenada"): "La Plata",
         ("Buenos Aires", "C. de M. Leonardo Rosales"): "Bahía Blanca", ("Buenos Aires", "Leandro N. Alem"): "Lincoln",
         ("Buenos Aires", "Tres Arroyos"): "Necochea", ("Buenos Aires", "Juárez"): "Necochea", ("Buenos Aires", "González Chaves"): "Necochea",
         ("Córdoba", "General Roca"): "Juárez Celmán", ("Córdoba", "Pte. Roque Saenz Peña"): "Juárez Celmán",
         ("Salta", "General José de San Martín"): "Orán", ("Mendoza", "General Alvear"): "San Rafael", ("Mendoza", "Malargüe"): "San Rafael",
         ("San Juan", "Chimbas"): "Capital"}
# 1954 -> nombre de 1958 (cambios de nombre posteriores a 1955 y variantes de escritura)
NOMBRE = {("Chaco", "12 de Abril"): "12 de Octubre", ("Chaco", "Cabo Mayor Farina"): "Mayor Luis J. Fontana",
          ("Chaco", "Güemes"): "General Güemes", ("Chaco", "24 de Febrero"): "Tapenagá",
          ("Chubut", "Paso de los Indios"): "Paso de Indios", ("Córdoba", "Ischilín"): "Ischillín", ("Formosa", "Capital"): "Formosa",
          ("La Pampa", "Leventué"): "Loventué", ("Misiones", "General Belgrano"): "General Manuel Belgrano",
          ("Salta", "General Güemes"): "General Martín Miguel de Güemes", ("Santa Cruz", "Corpe-Aike"): "Corpen Aike"}
# Fuera del análisis: sin padrón en 1954 (zona militar de Comodoro Rivadavia: Escalante, Sarmiento y Río Senguerr de Chubut y
# el norte de Deseado y Lago Buenos Aires), sin tabla total (San Luis y Tucumán: solo varones) o sin 1958 por departamento
# (Corrientes, Río Negro); unidades de 1958 sin contraparte en 1954 (Susques, Los Andes, Zonda: no tomadas en cuenta).
FUERA58 = {("Chubut", "Escalante"), ("Chubut", "Sarmiento"), ("Chubut", "Río Senguerr"), ("Santa Cruz", "Deseado"),
           ("Santa Cruz", "Lago Buenos Aires"), ("Jujuy", "Susques"), ("Salta", "Los Andes"), ("San Juan", "Zonda")}
FUERA54 = {("Santa Cruz", "Deseado"), ("Santa Cruz", "Lago Buenos Aires")}
# 1965: partidos nuevos de Buenos Aires (1960-61) y Misiones, que se redividió entera (17 departamentos contra 11)
GRUPO65 = {("Buenos Aires", "Berazategui"): "Quilmes", ("Buenos Aires", "Capitán Sarmiento"): "Bartolomé Mitre",
           ("Buenos Aires", "Salliqueló"): "Pellegrini", ("Buenos Aires", "3 de Febrero"): "General San Martín",
           ("Buenos Aires", "Escobar"): "Pilar", ("Buenos Aires", "Hipólito Irigoyen"): "Pehuajó",
           ("Buenos Aires", "San Cayetano"): "Necochea", ("Corrientes", "General Alvear"): "San Martín",
           # grafías de 1965 distintas de las de 1958
           ("Córdoba", "Ischilín"): "Ischillín", ("La Pampa", "Conhelo"): "Conhello", ("La Pampa", "Curacó"): "Cura-Có",
           ("Santa Fe", "Nueve de Julio"): "9 de Julio"}
# Escobar/Pilar e Hipólito/Pehuajó son claves intermedias: correspondencias.apply_pair
# agrega después todos los partidos de origen que documenta Cacopardo (PDF67–68).
TODA = {"Misiones"}                        # 1965: la provincia entera como una unidad (en los dos años)
SIN_TOTAL = ["Comodoro Rivadavia", "San Luis", "Tucumán"]
SIN_DEST = {1958: ["Corrientes", "Río Negro"], 1965: ["Jujuy", "Salta"]}     # sin datos por departamento en el destino
SOLO_VM = {("Misiones", "Concepción")}     # el total impreso repite las cifras de San Ignacio: se usa varones + mujeres


def norm(s):
    return " ".join(unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().upper().replace(".", " ").replace("-", " ").split())


def tabla54(dest):
    d = pd.read_csv(os.path.join(ROOT, "canton1954", "canton_1954.csv"))
    d = d[~d.provincia.isin(SIN_TOTAL + SIN_DEST[dest])]
    P = {c: d[d.categoria == c].pivot_table(index=["provincia", "unidad"], columns="concepto", values="valor", aggfunc="first")
         for c in ("varones solamente", "mujeres solamente", "varones y mujeres")}
    T, V, M = P["varones y mujeres"], P["varones solamente"], P["mujeres solamente"]
    log = []
    for k in T.index:
        if T.loc[k].isna().all(): continue
        if k in SOLO_VM:
            T.loc[k] = V.loc[k] + M.loc[k]; log.append("%s %s: varones + mujeres (total repetido)" % k); continue
        vm = V.loc[k] + M.loc[k] if k in V.index and k in M.index else None
        if vm is None: continue
        votos = [c for c in T.columns if c not in ("Inscriptos", "Votantes")]
        for c in T.columns:
            if pd.isna(T.loc[k, c]) or pd.isna(vm[c]) or T.loc[k, c] == vm[c] or c == "Inscriptos": continue
            res = lambda r: r["Votantes"] - r[votos].fillna(0).sum()
            alt = T.loc[k].copy(); alt[c] = vm[c]
            if abs(res(alt)) < abs(res(T.loc[k])):    # la fila del total cierra con varones + mujeres: el total impreso es el que falla
                log.append("%s %s, %s: %d -> %d" % (k[0], k[1], c, T.loc[k, c], vm[c])); T.loc[k, c] = vm[c]
    return T.dropna(how="all"), log


def main(dest=1958):
    import datos
    T, log = tabla54(dest)
    sfx = "p" if dest == 1958 else "d"
    toda = TODA if dest == 1965 else set()
    grupo = {**GRUPO, **(GRUPO65 if dest == 1965 else {})}
    v54, e54 = [], {}
    for (p, u), r in T.iterrows():
        if (p, u) in FUERA54 or pd.isna(r.get("Inscriptos")): continue
        nombre = p if p in toda else NOMBRE.get((p, u), u); key = (COD[p], 0, norm(nombre))
        e54[key] = e54.get(key, 0) + r["Inscriptos"]
        for c, val in r.items():
            if c in ("Inscriptos", "Votantes") or pd.isna(val): continue
            tipo = "EN BLANCO" if c.startswith("Blanco") else "POSITIVO"
            ag = "PERONISTA" if c == "Partido Peronista" else "UCR" if c == "Unión Cívica Radical" else "OTRO " + c.upper()
            v54.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id="" if tipo != "POSITIVO" else ag, votos_tipo=tipo, v=val))
    T58, _ = datos.cargar_todo(); U = datos.unidades(T58, dest)
    v58, e58 = [], {}
    for (p, u), r in U.items():
        if p not in COD or (p, u) in FUERA58 or not isinstance(r["ins"], int): continue
        key = (COD[p], 0, norm(p if p in toda else grupo.get((p, u), u)))
        e58[key] = e58.get(key, 0) + r["ins"]
        for b, val in r["bloc"].items():
            if dest == 1958: ag = "UCRI" if b in ("UCRI", "URB") else "UCRP" if b == "UCRP" else "OTRO " + str(b)
            else: ag = b if b in ("UP", "MPP", "UCRP", "MID", "UCRI", "FNPC") else "OTRO " + str(b)
            v58.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id=ag, votos_tipo="POSITIVO", v=val))
        v58.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id="", votos_tipo="EN BLANCO", v=r["bla"] + r["nul"]))
    idx = ["distrito_id", "seccion_id", "circuito"]
    for nombre, v, e in (("1954" + sfx, v54, e54), ("%d%s" % (dest, sfx), v58, e58)):
        v = pd.DataFrame(v).groupby(idx + ["agrupacion_id", "votos_tipo"]).v.sum().reset_index()
        e = pd.Series(e); e.index = pd.MultiIndex.from_tuples(e.index, names=idx)
        pd.to_pickle((v, e), os.path.join(HERE, "circ_%s.pkl" % nombre))
        print(nombre, "unidades", len(e), "electores", int(e.sum()), "votos", int(v.v.sum()))
    k54, k58 = set(e54), set(e58)
    print("solo 1954:", sorted(k54 - k58)); print("solo destino:", sorted(k58 - k54))
    print("correcciones del total con varones + mujeres:"); print("\n".join("  " + l for l in log))


if __name__ == "__main__":
    main(*[int(a) for a in sys.argv[1:2]])
