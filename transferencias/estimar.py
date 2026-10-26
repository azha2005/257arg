"""Transferencias de voto entre legislativas (diputados nacionales) por inferencia ecologica a nivel circuito.
    python transferencias/estimar.py 2021 2025
    python transferencias/estimar.py 2023 2025
    python transferencias/estimar.py 2019p 2023p     # presidente (circ_<anio>p.pkl de agregar_circuitos.py)
    python transferencias/estimar.py 2023p 2023b     # primera vuelta -> balotaje 2023
Necesita transferencias/circ_<anio>.pkl (agregar_circuitos.py; 2003-2009: agregar_polar_circuitos.py) y mapa<anio>/mapeo_listas_<anio>.csv (bloques de Wikipedia).
Salidas en transferencias/<origen>_<destino>/: matriz_votos.csv, matriz_pct.csv, intervalos.csv, por_provincia.csv,
calvo_nacional.csv (la variante identica al R: una sola matriz, circuitos sin ponderar) y control.json."""
import os, sys, json, glob, unicodedata
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")      # un hilo de BLAS por proceso: el paralelismo va por procesos
from concurrent.futures import ProcessPoolExecutor
import caba_cruce
import correspondencias
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rxc_calvo import fit, fractions
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")

# Bloques de cada año (codigo de la tabla de Wikipedia en mapeo_listas) -> categoria del analisis.
CAT = {2009: {"Frente para la Victoria (FPV) o al kirchnerismo": "Frente para la Victoria",
              "Acuerdo Cívico y Social (UCR-PS-ARI)": "Acuerdo Cívico y Social",
              "Propuesta Republicana (PRO) y aliados": "PRO / Unión-PRO",
              "Peronismo Federal o aliados": "Peronismo Federal", "Movimiento Proyecto Sur (SUR)": "Proyecto Sur"},
       2011: {"B01": "Frente para la Victoria", "B03": "UDESO (UCR)", "B02": "FAP", "B04": "Frente Popular / PRO",
              "B05": "Compromiso Federal", "B06": "CC-ARI", "B07": "FIT"},
       2013: {"FPV": "Frente para la Victoria", "FPCyS": "FPCyS / UNEN", "FR": "Frente Renovador",
              "PRO": "PRO", "FIT": "FIT", "UxC": "Unión por Córdoba"},
       2019: {"B01": "Frente de Todos", "B02": "Juntos por el Cambio", "B03": "Consenso Federal", "B04": "FIT-U"},
       2017: {"B01": "Cambiemos", "B02": "Unidad Ciudadana", "B03": "Peronismo no kirchnerista", "B04": "1País",
              "B05": "FIT"},
       2021:{"B02": "Frente de Todos", "B01": "Juntos por el Cambio", "B04": "Libertarios (AL + LLA)",
              "B05": "FIT-U", "B03": "Tercera Vía / PF"},
       2023: {"B01": "Unión por la Patria", "B02": "La Libertad Avanza", "B03": "Juntos por el Cambio",
              "B04": "Hacemos", "B05": "FIT-U"},
       2025: {"B01": "La Libertad Avanza", "B02": "Fuerza Patria", "B03": "Provincias Unidas", "B04": "FIT-U"},
       # presidente: la clave es el nombre de la agrupacion
       "2011p": {"ALIANZA FRENTE PARA LA VICTORIA": "Frente para la Victoria", "ALIANZA FRENTE AMPLIO PROGRESISTA": "FAP",
                 "ALIANZA UNIÓN PARA EL DESARROLLO SOCIAL": "UDESO (UCR)", "ALIANZA COMPROMISO FEDERAL": "Compromiso Federal",
                 "ALIANZA FRENTE POPULAR": "Frente Popular", "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "FIT",
                 "COALICIÓN CÍVICA - AFIRMACIÓN PARA UNA REPÚBLICA IGUALITARIA ARI": "CC-ARI"},
       "2015p": {"ALIANZA FRENTE PARA LA VICTORIA": "Frente para la Victoria", "ALIANZA CAMBIEMOS": "Cambiemos",
                 "ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA)": "UNA (Massa)", "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "FIT",
                 "ALIANZA PROGRESISTAS": "Progresistas", "ALIANZA COMPROMISO FEDERAL": "Compromiso Federal"},
       "2015b": {"FRENTE PARA LA VICTORIA": "Frente para la Victoria", "CAMBIEMOS": "Cambiemos"},
       "2019p": {"FRENTE DE TODOS": "Frente de Todos", "JUNTOS POR EL CAMBIO": "Juntos por el Cambio",
                 "CONSENSO FEDERAL": "Consenso Federal", "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "FIT-U",
                 "FRENTE NOS": "NOS + Unite", "UNITE POR LA LIBERTAD Y LA DIGNIDAD": "NOS + Unite"},
       # Canton 1954 (diputados) y 1958 (presidente), por departamento: canton_1954_1958.py
       "1954p": {"PERONISTA": "Partido Peronista", "UCR": "UCR"},
       "1958p": {"UCRI": "UCRI (Frondizi)", "UCRP": "UCRP (Balbín)"},
       "2003p": {"0135": "Kirchner (FPV)", "0133": "Menem (Lealtad)", "0131": "López Murphy (Recrear)",
                 "0132": "Rodríguez Saá (MNP)", "0134": "Carrió (ARI)"},
       2005: {"B01": "Frente para la Victoria", "B02": "UCR y aliados", "B03": "Peronismo Federal",
              "B04": "ARI y aliados", "B05": "PRO", "B06": "FPCyS (Santa Fe)"},
       "2007p": {"0134": "Cristina Kirchner (FPV)", "0059": "Carrió (CC)", "0131": "Lavagna (UNA)", "0133": "Rodríguez Saá (FREJULI)"},
       "1958d": {"UCRI": "UCRI (Frondizi)", "UCRP": "UCRP (Balbín)"},
       "1962d": {"FJ": "UP y neoperonistas", "UCRI": "UCRI", "UCRP": "UCRP", "FNPC": "FNPC (centro)"},
       "1954d": {"PERONISTA": "Partido Peronista", "UCR": "UCR"},
       "1965d": {"UP": "UP y neoperonistas", "MPP": "UP y neoperonistas", "UCRP": "UCRP", "MID": "MID", "UCRI": "UCRI", "FNPC": "FNPC (centro)"},
       # Cantón 1930-1946 por departamento: canton_1930_1946.py
       "1930d": {"UCR": "UCR (yrigoyenismo)", "CD": "Conservadores", "RAN": "Antipersonalistas", "PS": "Socialistas"},
       "1937d": {"UCR": "UCR (Alvear)", "CON": "Concordancia (Ortiz)", "PS": "Socialista"},
       "1940d": {"UCR": "UCR", "CON": "Concordancia", "PS": "Socialista"},
       "1946d": {"PER": "Perón", "UD": "Unión Democrática", "PDN": "Demócrata Nacional"},
       # Córdoba por circuito, 1983-2001 (Ernesto Calvo; votos emitidos, sin «No votó»): cordoba_circuitos.py
       "1983pc": {"UCR": "UCR (Alfonsín)", "PJ": "PJ (Luder)", "PI": "PI"},
       "1983c": {"UCR": "UCR", "PJ": "PJ", "PI": "PI"},
       "1985c": {"UCR": "UCR", "PJ": "PJ", "PI": "PI", "UCEDE": "UCeDé"},
       "1987c": {"UCR": "UCR", "PJ": "PJ", "UCEDE": "UCeDé"},
       "1991c": {"UCR": "UCR", "PJ": "PJ", "UCEDE": "UCeDé", "CFI": "CFI"},
       "1993c": {"UCR": "UCR", "PJ": "PJ", "UCEDE": "UCeDé", "MODIN": "MODIN"},
       "1995pc": {"PJ": "PJ (Menem)", "UCR": "UCR (Massaccesi)", "FREPASO": "FREPASO (Bordón)", "UCEDE": "UCeDé"},
       "1995c": {"PJ": "PJ", "UCR": "UCR", "FREPASO": "FREPASO", "UCEDE": "UCeDé"},
       "1997c": {"UCR": "UCR", "PJ": "PJ", "FREPASO": "FREPASO", "AR": "Acción por la República", "UCEDE": "UCeDé"},
       "1999pc": {"ALIANZA": "Alianza (De la Rúa)", "PJ": "PJ (Duhalde)", "AR": "AR (Cavallo)", "UCEDE": "UCeDé"},
       "1999c": {"ALIANZA": "Alianza", "PJ": "PJ", "AR": "Acción por la República", "UCEDE": "UCeDé", "NM": "Nuevo Movimiento"},
       "2001c": {"PJ": "PJ", "UCR": "UCR", "UCEDE": "UCeDé", "MAV": "Acción Vecinal"},
       "2023b": {"UNION POR LA PATRIA": "Unión por la Patria", "LA LIBERTAD AVANZA": "La Libertad Avanza"},
       "2023p": {"UNION POR LA PATRIA": "Unión por la Patria", "LA LIBERTAD AVANZA": "La Libertad Avanza",
                 "JUNTOS POR EL CAMBIO": "Juntos por el Cambio", "HACEMOS POR NUESTRO PAIS": "Hacemos",
                 "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "FIT-U"}}
CAT["2023pp"] = {"UNION POR LA PATRIA | A- CELESTE Y BLANCA": "Massa (UxP)", "UNION POR LA PATRIA | B- JUSTA Y SOBERANA": "Grabois (UxP)",
                 "LA LIBERTAD AVANZA | A- LIBERTAD POR SIEMPRE": "Milei (LLA)",
                 "JUNTOS POR EL CAMBIO | B- LA FUERZA DEL CAMBIO": "Bullrich (JxC)", "JUNTOS POR EL CAMBIO | A- EL CAMBIO DE NUESTRAS VIDAS": "Larreta (JxC)",
                 "HACEMOS POR NUESTRO PAIS | A- HACEMOS": "Schiaretti (Hacemos)",
                 "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD | A- UNIR Y FORTALECER LA IZQUIERDA": "FIT-U",
                 "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD | B- UNIDAD DE LUCHADORES Y LA IZQUIERDA": "FIT-U"}   # PASO presidencial 2023 por lista
CAT["2003pc"] = CAT["2003p"]     # Córdoba 2003 sin «No votó», para empalmar con cordoba_circuitos.py
CAT["1999pe"] = {"DLR": "Alianza (De la Rúa)", "DUH": "PJ (Duhalde)", "CAV": "AR (Cavallo)"}   # presidente_1999.py: por candidato
CAT["2003pe"] = CAT["2003p"]     # nacional sobre votos emitidos (1999 -> 2003 como Calvo y Escolar)
EXTRA = ["Otros", "Blanco y nulo", "No votó"]
CAT['1989p'] = {'MEN':'PJ (Menem)', 'ANG':'UCR (Angeloz)', 'ALS':'Alianza de Centro', 'EBO':'Unidad Socialista', 'MPN':'MPN'}
CAT['1995p'] = {'MEN':'PJ (Menem)', 'BOR':'FREPASO (Bordón)', 'MAS':'UCR (Massaccesi)'}
CAT['1989d'] = {'PJ':'PJ', 'UCR':'UCR', 'ADC':'Alianza de Centro', 'CFI':'CFI', 'IU':'Izquierda Unida', 'US':'Unidad Socialista', 'FR':'Fuerza Republicana', 'MPN':'MPN'}
CAT['1994c'] = {'PJ':'PJ', 'UCR':'UCR', 'FG':'Frente Grande', 'MOD':'MODIN', 'PD':'PD', 'PAL':'PAL', 'FR':'Fuerza Republicana', 'MPN':'MPN', 'MPJ':'MPJ', 'PRS':'PRS', 'CI':'Convocatoria Independiente'}
CAT['1985d'] = {'UCR':'UCR','PJ':'PJ','REN':'Peronismo renovador','PI':'PI','UCD':'UCeDé','FDP':'Frente del Pueblo','PAL':'PAL','PRS':'PRS','BLO':'Bloquista','MPN':'MPN'}
CAT['1987d'] = {'PJ':'PJ','UCR':'UCR','UCD':'UCeDé','FAP':'FAP (Catamarca)','PAL':'PAL','MPN':'MPN','ABL':'Bloquista','PPR':'PPR'}
CAT['1983p'] = {'UCR':'UCR (Alfonsín)','PJ':'PJ (Luder)','PI':'PI','MID':'MID','AF':'Alianza Federal','PAL':'PAL','BLO':'Bloquista','MPN':'MPN','MFP':'MOFEPA'}
CAT['1997d'] = {'ALI':'Alianza','PJ':'PJ','AR':'Acción por la República','FR':'Fuerza Republicana','PD':'PD','PN':'Partido Nuevo','MPN':'MPN','PDJ':'Desarrollo y Justicia'}
CAT['1999p'] = CAT['1999pe']
CAT['1914d'] = {'UCR':'UCR','CON':'Conservadores','SOC':'Socialistas','UC':'Unión Cívica','IND':'Independientes (Peña)'}
# UCR queda como referencia: tiene datos positivos en todas las provincias comparables.
CAT['1916d'] = {'CON':'Conservadores','SOC':'Socialistas','PDP':'PDP','SAR':'Socialista Argentino','RAD':'Radicales disidentes','CCI':'Concentración Cívica','UCR':'UCR'}
CAT['1916de'] = CAT['1916d']
# Nombres de seccion que cambian entre anios: (distrito, nombre) -> nombre de 2023/2025.
ALIAS = {("21", "VILLA CONSTITUCION"): "CONSTITUCION", ("21", "NUEVE DE JULIO"): "9 DE JULIO",
         ("19", "PEDERNERA"): "GENERAL PEDERNERA", ("19", "PRINGLES"): "CORONEL PRINGLES",
         ("19", "PUEYRREDON"): "JUAN MARTIN DE PUEYRREDON", ("19", "SAN MARTIN"): "LIBERTADOR GENERAL SAN MARTIN",
         ("19", "GOBERNADOR DUPUY"): "DUPUY"}
# Secciones sin nombre en los ambitos (2011 y 2013): subsecciones de Santa Fe; por padron, 10 es La Capital, 14 y 15 son Rosario.
SECFIX = {("21", 10): "LA CAPITAL", ("21", 14): "ROSARIO", ("21", 15): "ROSARIO"}
DISTRITOS = {"01": "Ciudad de Buenos Aires", "02": "Buenos Aires", "03": "Catamarca", "04": "Córdoba", "05": "Corrientes",
             "06": "Chaco", "07": "Chubut", "08": "Entre Ríos", "09": "Formosa", "10": "Jujuy", "11": "La Pampa", "12": "La Rioja",
             "13": "Mendoza", "14": "Misiones", "15": "Neuquén", "16": "Río Negro", "17": "Salta", "18": "San Juan", "19": "San Luis",
             "20": "Santa Cruz", "21": "Santa Fe", "22": "Santiago del Estero", "23": "Tucumán", "24": "Tierra del Fuego"}
COBERTURA = 0.9          # si los circuitos comunes cubren menos que esto del padron de la provincia, se usa la seccion
BOOT = int(os.environ.get("BOOT", 200))
WORKERS = int(os.environ.get("WORKERS", 4))   # pocos procesos: la CPU no pasa de temperatura normal
RATIO = (0.75, 1.33)      # cambio admitido de electores del circuito, relativo al crecimiento mediano del padron
if "RATIO" in os.environ:   # p. ej. RATIO=0.6,2.3 para 1954-58: el conurbano crecio mucho mas que el resto en cuatro anios
    RATIO = tuple(float(x) for x in os.environ["RATIO"].split(","))
LAMBDAS = (2e-4, 2e-5, 2e-6, 2e-7, 0)   # penalizacion por circuito (pesos de media 1) hacia la matriz nacional;
                                        # se elige la mas fuerte cuyo error en validacion cruzada (5 grupos de circuitos
                                        # por provincia) queda a menos de 1 % del minimo
LAMBDA = float(os.environ["LAMBDA"]) if "LAMBDA" in os.environ else None


def secnames(anio):
    """(distrito, seccion_id) -> nombre de seccion normalizado, de los archivos de ambitos de la DINE."""
    anio = int(str(anio).rstrip("pbdce"))
    f = glob.glob(os.path.join(ROOT, "datos_oficiales", str(anio), "x", "**", "*mbito*.csv"), recursive=True)
    if f:
        a = pd.read_csv(f[0], dtype=str).dropna(subset=["seccion_id"])
    elif os.path.exists(os.path.join(HERE, "secciones_%d.csv" % anio)):   # PolAr (2003-2009): nombres de agregar_polar_circuitos.py
        a = pd.read_csv(os.path.join(HERE, "secciones_%d.csv" % anio), dtype=str).rename(columns={"depto": "seccion_nombre"})
    else:   # Canton (1954, 1958): la unidad ya es el departamento
        return {}
    nm = a.seccion_nombre.map(lambda s: unicodedata.normalize("NFD", str(s).upper()).encode("ascii", "ignore").decode().strip())
    out = {}
    for d, i, n in zip(a.distrito_id, a.seccion_id, nm):
        d, i = "%02d" % int(d), int(i)
        if n in ("", "NAN"): n = SECFIX.get((d, i), n)
        out[(d, i)] = ALIAS.get((d, n), n)
    return out


def mapeo(anio):
    """(distrito, lista, codigo) de las listas de un anio. 2013 no tiene mapeo_listas: se lee LIST2BLOC de su build."""
    f = os.path.join(ROOT, "mapa%d" % anio, "mapeo_listas_%d.csv" % anio)
    if os.path.exists(f):
        m = pd.read_csv(f, dtype=str)
        if "grupo_wiki" in m:   # 2009: por nombre de distrito y grupo de la Wikipedia
            ids = {unicodedata.normalize("NFD", n).encode("ascii", "ignore").decode(): d for d, n in DISTRITOS.items()}
            m = m.assign(distrito=m.distrito_nombre.map(lambda n: ids[unicodedata.normalize("NFD", n).encode("ascii", "ignore").decode()]),
                         lista=m.agrupacion_id.str.zfill(4), codigo=m.grupo_wiki)
        return m
    src = open(os.path.join(ROOT, "mapa%d" % anio, "build_%d.py" % anio), encoding="utf8").read()
    i = src.index("LIST2BLOC = {}"); j = src.index("\n})", i) + 3
    ns = {"D2P": ["%02d" % k for k in range(1, 25)]}
    exec(src[i:j], ns)
    return pd.DataFrame([dict(distrito=d, lista=a, codigo=b) for (d, a), b in ns["LIST2BLOC"].items()])


def load(anio, raw=False):
    v, e = pd.read_pickle(os.path.join(HERE,'historicos_1989','raw_%s.pkl'%anio) if raw else os.path.join(HERE, "circ_%s.pkl" % anio))
    if str(anio).endswith(("p", "b", "d", "c", "e")):   # presidente (b: balotaje; d: diputados de Cantón): la agrupacion ya viene en el pkl
        m = pd.DataFrame([dict(distrito=d, lista=a, codigo=a) for d in DISTRITOS for a in v.agrupacion_id.unique()])
    else:
        m = mapeo(anio)
    cats = list(dict.fromkeys(CAT[anio].values())) + EXTRA
    v = v.merge(m[["distrito", "lista", "codigo"]], left_on=["distrito_id", "agrupacion_id"], right_on=["distrito", "lista"], how="left")
    t = v.votos_tipo.str.upper()
    v["cat"] = np.where(t == "POSITIVO", v.codigo.map(CAT[anio]).fillna("Otros"), "Blanco y nulo")
    key = ["distrito_id", "seccion_id", "circuito"]
    T = v.pivot_table(index=key, columns="cat", values="v", aggfunc="sum", fill_value=0)
    T = T.reindex(columns=cats, fill_value=0)
    T["No votó"] = e.reindex(T.index).fillna(0) - T[cats[:-1]].sum(1)
    cats = [c for c in cats if T[c].sum() > 0]     # sin columnas vacias (p. ej. Otros en presidente)
    return T[cats], cats


def to_sections(T, d, names):
    """Reemplaza los circuitos de la provincia d por sus secciones (departamentos), con el nombre como clave."""
    P = T.loc[[d]].copy()
    P.index = pd.MultiIndex.from_tuples([(d, 0, "S:" + names[(d, s)]) for d, s, _ in P.index], names=T.index.names)
    return pd.concat([T.drop(index=d, level=0), P.groupby(level=[0, 1, 2]).sum()]).sort_index()


def prepare(y0, y1):
    """Circuitos (o secciones) comunes y filtrados: X, Y en proporcion del padron, pesos y controles."""
    raw = (y0,y1) in [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]
    A, rows = load(y0,raw=raw); B, cols = load(y1,raw=raw)
    a0, a1 = (int(str(y).rstrip("pbdce")) for y in (y0, y1))
    if a0 > 1990 and a0 < caba_cruce.CORTE <= a1:   # Capital renumero sus circuitos en 2008: se cruza por circunscripcion
        A = caba_cruce.cruzar(A, a0)
        ev = A.loc["01"].sum(1).droplevel(0); ev.index = [int(c[1:]) for c in ev.index]
        B = caba_cruce.cruzar(B, a1, ev)
    ctl = dict(circuitos_origen=len(A), circuitos_destino=len(B), por_seccion=[])
    A, B, cruce = correspondencias.apply_pair(A, B, y0, y1)
    if cruce:
        ctl["correspondencias"] = cruce
    if y0=='1914d':ctl['base_medida']='votos de fuerzas/primer candidato publicado; cobertura territorial parcial; sin abstención ni blancos'
    n0, n1 = secnames(y0), secnames(y1)
    ec = A.loc[A.index.intersection(B.index)].sum(1).groupby(level=0).sum()
    cobertura = (ec / A.sum(1).groupby(level=0).sum()).fillna(0)
    for d, cov in cobertura.items():
        if cov < COBERTURA and n0:      # Cantón: ya es por departamento, no hay secciones
            A, B = to_sections(A, d, n0), to_sections(B, d, n1)
            ctl["por_seccion"].append(dict(distrito=d, cobertura_circuitos=round(float(cov), 3)))
    idx = A.index.intersection(B.index)
    ea, eb = A.loc[idx].sum(1), B.loc[idx].sum(1)
    crec = float((eb / ea)[ea > 0].median())       # crecimiento tipico del padron entre las dos elecciones
    nv = lambda T: T.loc[idx]["No votó"] if "No votó" in T else 0 * ea    # Córdoba 1983-2001: votos emitidos, sin «No votó»
    ok = (nv(A) >= 0) & (nv(B) >= 0) & (ea > 0) & (eb / ea / crec).between(*RATIO)
    if raw or (y0,y1) in [('1989p','1995p'),('1989d','1994c'),('1985d','1987d'),('1983p','1989p'),('1987d','1989p'),('1985d','1989p'),('1989p','1997d')]:
        problems = json.load(open(os.path.join(HERE,'historicos_1989','exclusiones.json'),encoding='utf8'))
        problems = [p for p in problems if p['anio'] in (y0,y1)]
        bad = {(p['distrito'],0,p.get('circuito_original',p['circuito']) if raw else p['circuito']) for p in problems}
        if raw: bad = {correspondencias.new_historical_key(k,y0,y1) for k in bad}
        if y1 == '1989p': bad = {correspondencias.common_early_key(k,y0) for k in bad}
        ok &= ~idx.isin(bad)
        ctl['exclusiones_calidad'] = problems
        ctl['base_medida'] = 'votos desglosados, sin abstención'
    usado = ea[ok].groupby(level=0).sum() / A.sum(1).groupby(level=0).sum()
    ctl.update(comunes=len(idx), usados=int(ok.sum()), crecimiento_padron_mediano=round(crec, 3), filtro_razon_crecimiento=list(RATIO),
               cobertura_por_provincia=usado.fillna(0).round(3).to_dict(),
               electores_origen_usados=int(ea[ok].sum()), electores_origen_total=int(A.sum(1).sum()),
               electores_destino_usados=int(eb[ok].sum()), electores_destino_total=int(B.sum(1).sum()),
               descartados=[dict(circuito="-".join(map(str, i)), electores_origen=int(ea[i]), electores_destino=int(eb[i])) for i in idx[~ok]][:400])
    A, B = A.loc[idx[ok]], B.loc[idx[ok]]
    ctl["unidades_por_provincia"] = {
        d: {"circuitos": sum(not c.startswith(("S:", "G:")) for _, _, c in g.index),
            "grupos_circuitos": sum(c.startswith("G:") for _, _, c in g.index),
            "departamentos": sum(c.startswith("S:") for _, _, c in g.index)}
        for d, g in A.groupby(level=0)}
    XA = A.div(A.sum(1), axis=0); YB = B.div(B.sum(1), axis=0)
    w = B.sum(1) / B.sum(1).mean()                 # peso: electores del circuito en la eleccion de destino (media 1)
    return A, B, XA, YB, w, rows, cols, ctl


def fit_prov(X, Y, const, w, g0):
    """Ajuste provincial sin destinos ausentes: las columnas sin votos en la provincia (fuerzas que no se presentaron)
    quedan en cero y no reciben flujo heredado de la matriz nacional. La ultima columna (No voto) siempre esta."""
    keep = (w[:, None] * Y).sum(0) > 0; keep[-1] = True
    G0 = g0.reshape(X.shape[1], -1)[:, keep[:-1]].ravel()
    Bk = fit(X, Y[:, keep], const=const, w=w, g0=G0)
    B = np.zeros((X.shape[1], Y.shape[1])); B[:, keep] = Bk
    return B


def _cv_task(args):
    """Error fuera de muestra de una penalizacion en una provincia (suma ponderada de cuadrados y suma de pesos)."""
    lam, Xd, Yd, wd, fd, g0, folds = args
    err = tot = 0
    for k in range(folds):
        tr, te = fd != k, fd == k
        if te.sum() == 0 or tr.sum() < 5: continue
        Bp = fit_prov(Xd[tr], Yd[tr], lam * tr.sum(), wd[tr], g0)
        err += (wd[te, None] * (Xd[te] @ Bp - Yd[te])[:, :-1] ** 2).sum(); tot += wd[te].sum()
    return lam, err, tot


def cv_lambda(XA, YB, w, g0, pool, folds=5):
    """Error de prediccion (pp por columna) fuera de muestra de cada penalizacion; circuitos repartidos al azar en grupos."""
    fold = pd.Series(np.random.default_rng(1).integers(0, folds, len(XA)), index=XA.index)
    tasks = [(lam, XA.loc[d].values, YB.loc[d].values, w.loc[d].values, fold.loc[d].values, g0, folds)
             for lam in LAMBDAS for d in XA.index.get_level_values(0).unique()]
    acc = {lam: [0, 0] for lam in LAMBDAS}
    for lam, e, t in pool.map(_cv_task, tasks):
        acc[lam][0] += e; acc[lam][1] += t
    return {lam: float(np.sqrt(e / t / (YB.shape[1] - 1)) * 100) for lam, (e, t) in acc.items()}


def _boot_task(args):
    """Una replica bootstrap: remuestrea circuitos dentro de cada provincia y suma las matrices provinciales."""
    b, data, lam, g0 = args
    rng = np.random.default_rng([2025, b]); S = 0
    for Xp, Yp, wp, Vp in data:
        k = rng.integers(0, len(Xp), len(Xp))
        cnt = np.bincount(k, minlength=len(Xp))           # remuestrear filas = pesar cada circuito por sus repeticiones
        S = S + fit_prov(Xp, Yp, lam * len(k), wp * cnt, g0) * Vp[:, None]   # totales de la provincia fijos
    return S


def main(y0, y1, out=None):
    out = out or os.path.join(HERE, "%s_%s" % (y0, y1)); os.makedirs(out, exist_ok=True)
    A, B, XA, YB, w, rows, cols, ctl = prepare(y0, y1)
    if ctl.get("correspondencias"):
        pd.DataFrame(ctl["correspondencias"]["registros"]).to_csv(os.path.join(out, "correspondencias.csv"), index=False, encoding="utf-8-sig")
    pool = ProcessPoolExecutor(WORKERS)

    # 1) Variante Calvo: una matriz nacional, circuitos sin ponderar, penalizacion 0.001 hacia cero.
    Bc = fit(XA.values, YB.values, const=0.001)
    V = XA.mul(B.sum(1), axis=0)                   # padron de destino repartido segun el voto de origen del circuito
    calvo = pd.DataFrame(Bc * V.sum().values[:, None], index=rows, columns=cols)
    calvo.round().astype(int).to_csv(os.path.join(out, "calvo_nacional.csv"), encoding="utf-8-sig")

    # 2) Principal: matriz nacional ponderada como centro, luego una matriz por provincia penalizada hacia ella.
    Bn = fit(XA.values, YB.values, const=0.001, w=w.values)
    g0 = np.log(Bn[:, :-1] / Bn[:, -1:]).ravel()
    if LAMBDA is None:
        cv = cv_lambda(XA, YB, w, g0, pool)
        lam = max(k for k, v in cv.items() if v <= 1.01 * min(cv.values()))   # la mas fuerte a menos de 1 % del minimo
        ctl["validacion_cruzada_pp"] = {str(k): round(v, 4) for k, v in cv.items()}
    else:
        lam = LAMBDA
    ctl["lambda"] = lam

    def prov(Xp, Yp, wp, Vp):
        Bp = fit_prov(Xp, Yp, lam * len(wp), wp, g0)
        return Bp * Vp[:, None]

    provs = A.index.get_level_values(0).unique()
    parts = {d: prov(XA.loc[d].values, YB.loc[d].values, w.loc[d].values, V.loc[d].sum().values) for d in provs}
    M = sum(parts.values())
    mat = pd.DataFrame(M, index=rows, columns=cols)
    mat.round().astype(int).to_csv(os.path.join(out, "matriz_votos.csv"), encoding="utf-8-sig")
    (mat.div(mat.sum(1), axis=0) * 100).round(1).to_csv(os.path.join(out, "matriz_pct.csv"), encoding="utf-8-sig")
    pp = []
    for d, P in parts.items():
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                pp.append(dict(distrito=d, origen=r, destino=c, votos=round(P[i, j])))
    pd.DataFrame(pp).to_csv(os.path.join(out, "por_provincia.csv"), index=False, encoding="utf-8-sig")

    # 3) Bootstrap en paralelo: se remuestrean circuitos dentro de cada provincia (la matriz nacional de centro queda fija).
    data = [(XA.loc[d].values, YB.loc[d].values, w.loc[d].values, V.loc[d].sum().values) for d in provs]
    boots = list(pool.map(_boot_task, [(b, data, lam, g0) for b in range(BOOT)], chunksize=max(1, BOOT // (4 * WORKERS))))
    pool.shutdown()
    boots = np.array(boots)
    lo, hi = np.percentile(boots, 5, axis=0), np.percentile(boots, 95, axis=0)
    iv = [dict(origen=r, destino=c, votos=round(M[i, j]), p5=round(lo[i, j]), p95=round(hi[i, j]))
          for i, r in enumerate(rows) for j, c in enumerate(cols)]
    pd.DataFrame(iv).to_csv(os.path.join(out, "intervalos.csv"), index=False, encoding="utf-8-sig")

    # Controles: ajuste de las marginales y distancia entre la variante principal y la de Calvo.
    pred = (XA.values @ (M / M.sum(1, keepdims=True)))
    ctl.update(rmse_destino_pp=float(np.sqrt(np.average(((pred - YB.values) * 100) ** 2, axis=0, weights=w)).mean()),
               votos_distintos_vs_calvo=int(np.abs(M - calvo.values).sum() / 2), votos_total=int(M.sum()),
               marginal_origen=A.sum().astype(int).to_dict(), marginal_destino=B.sum().astype(int).to_dict(),
               marginal_destino_provincia={d: g.sum().astype(int).to_dict() for d, g in B.groupby(level=0)},
               marginal_destino_estimada=dict(zip(cols, M.sum(0).round().astype(int).tolist())))
    json.dump(ctl, open(os.path.join(out, "control.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    pd.set_option("display.width", 250)
    print(json.dumps({k: v for k, v in ctl.items() if k != "descartados"}, ensure_ascii=False, indent=1))
    print((mat.div(mat.sum(1), axis=0) * 100).round(1).to_string())
    print(mat.round(-3).astype(int).to_string())


if __name__ == "__main__":
    main(*[a if a.endswith(("p", "b", "d", "c", "e")) else int(a) for a in sys.argv[1:3]])
