"""Catálogo de todas las elecciones y tablas por unidad para el explorador de sankeys.

Dos fuentes:
- `transferencias/circ_<clave>.pkl` (56 elecciones, por circuito o departamento, categorías curadas en CAT de estimar.py).
- `resultados_xlsx/MASTER_resultados.xlsx`, hoja `largo` (todas las elecciones del índice, por departamento o sección).
  Leerla tarda ~2 min: se guarda en cache/master.pkl y se regenera si el xlsx es más nuevo.

`tabla(clave)` devuelve un DataFrame con índice (provincia, unidad normalizada) y columnas = categorías,
«Blanco y nulo» y, si hay electores, «No votó». Las categorías de MASTER salen del bloque de la Wikipedia
cuando la elección lo tiene y, si no, del partido; las chicas van a «Otros»."""
import os, re, sys, unicodedata, difflib
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.dirname(HERE); ROOT = os.path.dirname(TR)
sys.path.insert(0, TR)
import estimar                                    # noqa: E402  (CAT, DISTRITOS, load, secnames)

CACHE = os.path.join(HERE, "cache"); os.makedirs(CACHE, exist_ok=True)
MASTER = os.path.join(ROOT, "resultados_xlsx", "MASTER_resultados.xlsx")
DISTRITOS = estimar.DISTRITOS
PROVINCIAS = sorted(DISTRITOS.values(), key=lambda n: unicodedata.normalize("NFD", n).encode("ascii", "ignore"))
EXTRA = ["Otros", "Blanco y nulo", "No votó"]


def ascii_up(s):
    return unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().upper()


# --- provincias -------------------------------------------------------------------------------------------
_PROV = {re.sub(r"[^A-Z]", "", ascii_up(n)): n for n in DISTRITOS.values()}
_PROV.update({"CAPITALFEDERAL": "Ciudad de Buenos Aires", "CIUDADAUTONOMADEBUENOSAIRES": "Ciudad de Buenos Aires",
              "CIUDADAUTONOMABSAS": "Ciudad de Buenos Aires", "CABA": "Ciudad de Buenos Aires",
              "TIERRADELFUEGOANTARTIDAEISLASDELATLANTICOSUR": "Tierra del Fuego", "TIERRADELFUEGOAEIAS": "Tierra del Fuego",
              "COMODORORIVADAVIA": "Chubut"})       # zona militar de Comodoro Rivadavia (1944-1955): hoy Chubut y Santa Cruz


def prov_canon(n):
    k = re.sub(r"[^A-Z]", "", ascii_up(n))
    return _PROV.get(k, str(n))


# --- unidades ---------------------------------------------------------------------------------------------
_ABR = {"GRAL": "GENERAL", "GRL": "GENERAL", "GNERAL": "GENERAL", "CNEL": "CORONEL", "TTE": "TENIENTE",
        "PTE": "PRESIDENTE", "PDTE": "PRESIDENTE", "DR": "DOCTOR", "STA": "SANTA", "STO": "SANTO", "FRAY": "FRAY",
        "PNAS": "PIEDRAS", "CDTE": "COMANDANTE", "CMTE": "COMANDANTE", "ALTE": "ALMIRANTE", "ING": "INGENIERO", "LIB": "LIBERTADOR", "PCIA": "PRESIDENCIA", "PCIADE": "PRESIDENCIA",
        "UNO": "1", "PRIMERO": "1", "DOS": "2", "TRES": "3", "CUATRO": "4", "CINCO": "5", "NUEVE": "9", "DOCE": "12",
        "DIECISEIS": "16", "VEINTICINCO": "25", "VEINTE": "20"}
_FUERA = {"DEPARTAMENTO", "DEPTO", "DPTO", "PDO", "PARTIDO", "SECCION"}


def nk(s):
    """Clave normalizada de una unidad: sin tildes ni signos, abreviaturas expandidas, números sin ceros a la izquierda.
    «Cuarta Sección · San Rafael» (DINE 2011-2025) y «Capital - 481» (códigos de E. Calvo) quedan en el departamento."""
    s = str(s).split("·")[-1]
    s = re.sub(r"\s*-\s*\d+\s*$", "", s)
    s = ascii_up(s)
    if s.startswith("S:"): s = s[2:]
    w = [_ABR.get(t, t) for t in re.sub(r"[^A-Z0-9]", " ", s).split() if t not in _FUERA]
    w = [str(int(t)) if t.isdigit() else t for t in w]
    k = "".join(w)
    return {"LACAPITAL": "CAPITAL", "CIUDADCAPITAL": "CAPITAL", "CIUDAD": "CAPITAL"}.get(k, k)


# Departamentos que cambiaron de nombre (clave normalizada -> la de otros años), por provincia.
SINONIMOS = {"San Luis": {"PEDERNERA": "GENERALPEDERNERA", "PRINGLES": "CORONELPRINGLES", "DUPUY": "GOBERNADORDUPUY",
                          "JUANMARTINDEPUEYRREDON": "CAPITAL", "PUEYRREDON": "CAPITAL", "LACAPITAL": "CAPITAL",
                          "LIBERTADORGENERALSANMARTIN": "SANMARTIN"},
             "Jujuy": {"GENERALBELGRANO": "DOCTORMANUELBELGRANO", "BELGRANO": "DOCTORMANUELBELGRANO", "MANUELBELGRANO": "DOCTORMANUELBELGRANO", "CAPITAL": "DOCTORMANUELBELGRANO"},
             "Santa Fe": {"VILLACONSTITUCION": "CONSTITUCION"},
             "Chaco": {"CAPITAL": "SANFERNANDO", "UNION12DEOCTUBRE": "12DEOCTUBRE"},
             "Formosa": {"CAPITAL": "FORMOSA"}, "Neuquén": {"CAPITAL": "CONFLUENCIA"},
             "Entre Ríos": {"CAPITAL": "PARANA"},
             "Tierra del Fuego": {"ANTARTIDA": "ANTARTIDAARGENTINA", "SECTORANTARTICOARGENTINO": "ANTARTIDAARGENTINA", "UNIONUSHUAIA": "USHUAIA"}}


def nkp(prov, s):
    k = nk(s)
    return SINONIMOS.get(prov, {}).get(k, k)


# --- MASTER -------------------------------------------------------------------------------------------------
_master = None


def master():
    global _master
    if _master is None:
        f = os.path.join(CACHE, "master.pkl")
        if not os.path.exists(f) or (os.path.exists(MASTER) and os.path.getmtime(f) < os.path.getmtime(MASTER)):   # sin el xlsx (Space), vale la copia
            print("Leyendo MASTER_resultados.xlsx (una vez, ~2 min)...", flush=True)
            df = pd.read_excel(MASTER, sheet_name="largo", engine="openpyxl")
            df.drop(columns=["fuente"]).to_pickle(f)
        _master = pd.read_pickle(f)
    return _master


CARGO = {"presidente": "Presidente", "presidente_paso": "Presidente (PASO)", "presidente_balotaje": "Presidente (balotaje)",
         "diputados": "Diputados nacionales", "senadores": "Senadores nacionales", "senadores_nac": "Senadores nacionales",
         "diputados_prov": "Diputados provinciales", "senadores_prov": "Senadores provinciales", "gobernador": "Gobernador",
         "constituyentes": "Convencionales constituyentes", "vicepresidente": "Vicepresidente", "delegados": "Delegados"}
FUENTE = {"principal": "", "mujeres": "mujeres", "varones": "varones", "parciales": "parciales",
          "detalle_mendoza": "solo Mendoza, detalle", "detalle_corrientes": "solo Corrientes, detalle",
          "detalle_cordoba": "solo Córdoba, detalle", "entre_rios_oficial": "solo Entre Ríos, oficial",
          "datar_2003": "dat.ar", "circuito_AMBA": "AMBA por circuito"}

# Elecciones de los pkl: (año, descripción). La unidad es circuito salvo que diga otra cosa.
PKL = {"1914d": (1914, "Diputados (Cantón y actas)"), "1916d": (1916, "Diputados (Cantón y actas)"),
       "1916de": (1916, "Diputados, ampliado (Cantón y actas)"), "1930d": (1930, "Diputados (Cantón)"),
       "1937d": (1937, "Presidente (Cantón)"), "1940d": (1940, "Diputados (Cantón)"), "1946d": (1946, "Presidente (Cantón)"),
       "1954d": (1954, "Diputados (Cantón)"), "1954p": (1954, "Diputados, para cruzar con presidente (Cantón)"),
       "1958d": (1958, "Presidente, para cruzar con diputados (Cantón)"), "1958p": (1958, "Presidente (Cantón)"),
       "1962d": (1962, "Diputados (Cantón)"), "1965d": (1965, "Diputados (Cantón)"),
       "1983p": (1983, "Presidente (E. Calvo)"), "1985d": (1985, "Diputados (E. Calvo)"), "1987d": (1987, "Diputados (E. Calvo)"),
       "1989d": (1989, "Diputados (E. Calvo)"), "1989p": (1989, "Presidente (E. Calvo)"),
       "1994c": (1994, "Constituyentes (E. Calvo)"), "1995p": (1995, "Presidente (E. Calvo)"), "1997d": (1997, "Diputados (E. Calvo)"),
       "1999p": (1999, "Presidente (E. Calvo + Lupu–Stokes)"), "1999pe": (1999, "Presidente, votos emitidos (Calvo y Escolar)"),
       "2003pe": (2003, "Presidente, votos emitidos (Calvo y Escolar)"),
       "1983c": (1983, "Córdoba: diputados por circuito"), "1983pc": (1983, "Córdoba: presidente por circuito"),
       "1985c": (1985, "Córdoba: diputados por circuito"), "1987c": (1987, "Córdoba: diputados por circuito"),
       "1991c": (1991, "Córdoba: diputados por circuito"), "1993c": (1993, "Córdoba: diputados por circuito"),
       "1995c": (1995, "Córdoba: diputados por circuito"), "1995pc": (1995, "Córdoba: presidente por circuito"),
       "1997c": (1997, "Córdoba: diputados por circuito"), "1999c": (1999, "Córdoba: diputados por circuito"),
       "1999pc": (1999, "Córdoba: presidente por circuito"), "2001c": (2001, "Córdoba: diputados por circuito"),
       "2003pc": (2003, "Córdoba: presidente por circuito"),
       "2003p": (2003, "Presidente (PolAr)"), "2005": (2005, "Diputados (PolAr)"), "2007p": (2007, "Presidente (PolAr)"),
       "2009": (2009, "Diputados (PolAr)"), "2011": (2011, "Diputados (DINE)"), "2011p": (2011, "Presidente (DINE)"),
       "2013": (2013, "Diputados (DINE)"), "2015pp": (2015, "Presidente, PASO por lista (DINE)"),
       "2015p": (2015, "Presidente (DINE)"), "2015b": (2015, "Presidente, balotaje (DINE)"), "2017": (2017, "Diputados (DINE)"),
       "2019": (2019, "Diputados (DINE)"), "2019p": (2019, "Presidente (DINE)"), "2021": (2021, "Diputados (DINE)"),
       "2023pp": (2023, "Presidente, PASO por lista (DINE)"), "2023": (2023, "Diputados (DINE)"),
       "2023p": (2023, "Presidente (DINE)"), "2023b": (2023, "Presidente, balotaje (DINE)"), "2025": (2025, "Diputados (DINE)")}
DEPTO_PKL = lambda k: PKL[k][0] < 2003 and not k.endswith("c")    # los pkl anteriores a 2003 son por departamento


HIPOTETICOS = {"mapa1916fic", "mapa1985hip", "mapa2027", "mapa2027kic", "mapa2023massa"}
PASO_PRES = re.compile(r"^mapa(2011|2015|2019|2023)paso$")   # PASO presidenciales (las de 2013, 2017 y 2021 son de diputados)


def _atlas_files():
    import glob
    return sorted(glob.glob(os.path.join(ROOT, "mapas", "mapa*", "dataset_*.json")))


def _atlas_nombre(f, d):
    carpeta = os.path.basename(os.path.dirname(f)); base = os.path.basename(f)
    tit = re.sub(r"^Elecciones |de Argentina de$|\s+$", "", d.get("title", "")).strip()
    sub = (d.get("sets") or {}).get("1", {}).get("subtitle", "")
    extra = " (UCR + FREPASO sumados)" if "ucr_frepaso" in base else ""
    return "%s · %s%s%s · atlas %s" % (d.get("year"), tit, " · " + sub if sub else "", extra, carpeta[4:])


def catalogo():
    """Lista de elecciones: dict(id, anio, nombre, grupo, nivel)."""
    import json
    out = []
    for f in _atlas_files():
        d = json.load(open(f, encoding="utf8"))
        carpeta = os.path.basename(os.path.dirname(f))
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        hip = carpeta in HIPOTETICOS or "ucr_frepaso" in f
        out.append(dict(id="a:" + rel, anio=int(d.get("year")), nombre=_atlas_nombre(f, d),
                        grupo="Escenarios hipotéticos de los atlas (simulados, no son elecciones reales)" if hip
                        else "Atlas del proyecto (lo que muestra cada mapa: PASO, 1948, 1973…)", nivel="departamento"))
        if PASO_PRES.match(carpeta):
            out.append(dict(out[-1], id="a:" + rel + "#agrupacion", nombre=out[-1]["nombre"] + " (por agrupación)"))
            out[-2]["nombre"] += " (por precandidato)"
    for k in sorted(PKL, key=lambda k: (PKL[k][0], k)):
        if os.path.exists(os.path.join(TR, "circ_%s.pkl" % k)):
            out.append(dict(id="pkl:" + k, anio=PKL[k][0], nombre="%d · %s" % PKL[k],
                            grupo="Categorías curadas (las de los sankeys ya hechos)",
                            nivel="departamento" if DEPTO_PKL(k) else "circuito"))
    idx = pd.read_csv(os.path.join(ROOT, "resultados_xlsx", "indice_elecciones.csv"), encoding="utf-8-sig")
    m = master()
    hay = set(map(tuple, m.loc[m.tipo_fila.isin(["agrupacion", "candidato"]) & (m.votos > 0), ["anio", "cargo", "fuente_id"]].drop_duplicates().values))
    for r in idx.itertuples():
        if (r.anio, r.cargo, r.fuente_id) not in hay:      # sin votos en la hoja «largo» (AMBA 2025 por circuito: está en el atlas)
            continue
        f = FUENTE.get(r.fuente_id, r.fuente_id.replace("_", " "))
        c = CARGO.get(r.cargo, r.cargo.replace("otras_", "otras: ").replace("_", " "))
        out.append(dict(id="m:%d|%s|%s" % (r.anio, r.cargo, r.fuente_id), anio=int(r.anio),
                        nombre="%d · %s%s" % (r.anio, c, " (" + f + ")" if f else ""),
                        grupo="Todas las elecciones del MASTER (por departamento)", nivel=str(r.nivel)))
    return out


# --- tablas -------------------------------------------------------------------------------------------------
BN_TIPOS = ["blancos", "nulos", "impugnados", "recurridos", "impugnados_recurridos", "blancos_y_nulos"]
OTROS_RE = re.compile(r"^(OTROS|OTRAS)\b|SIN AGRUPAR|NO ATRIBUIDO|SIN DESAGREGAR")
_tablas = {}


def _familias():
    """Código de columna de la base de E. Calvo -> familia, de los atlas (FAMS de atlas_leg8399.py y FAM de 1997).
    {año: {código: nombre}}; para otro año se usa el mapa del año más cercano y, si falta el código, los demás."""
    src = open(os.path.join(ROOT, "comun", "atlas_leg8399.py"), encoding="utf8").read()
    ns = {}
    exec(src[src.index("FAMS={"):src.index("NATIONAL={")], ns)
    info = {k: v[0] for k, v in ns["INFO"].items()}
    info.update(PN="Partido Nuevo", PDJ="Desarrollo y Justicia", PO="Partido Obrero", PAIS="PAIS", PSA="Socialista Auténtico",
                PU="Partido Unidad", UCD="Unión del Centro Democrático", ALI="Alianza", FREP="FREPASO")
    out = {a: {c: info.get(b, b) for b, cs in f.items() for c in cs.split()} for a, f in ns["FAMS"].items()}
    s97 = open(os.path.join(ROOT, "mapas", "mapa1997", "build_1997.py"), encoding="utf8").read()
    ns = {}
    exec(s97[s97.index("FAM = {"):s97.index("CODE2BLOC = {")], ns)
    out[1997] = {c: info.get(b, b) for b, cs in ns["FAM"].items() for c in cs.split()}
    return out


FAMILIAS = _familias()


def familia(anio, code):
    if not isinstance(code, str) or not code: return None
    c = code.lower().strip(); c2 = re.sub(r"\d+$", "", c)
    for a in sorted(FAMILIAS, key=lambda a: abs(a - anio)):
        for k in (c, c2):
            if k in FAMILIAS[a]: return FAMILIAS[a][k]
    return None


def _unificar(etq, votos):
    """Variantes de la misma etiqueta («Partido Justicialista», «partido justicialista», «pj00») -> la más votada."""
    key = etq.map(lambda s: re.sub(r"\d+$", "", re.sub(r"[^a-z0-9]", "", ascii_up(s).lower())) or s)
    best = pd.DataFrame(dict(k=key, e=etq, v=votos)).groupby(["k", "e"]).v.sum().reset_index().sort_values("v").drop_duplicates("k", keep="last")
    nombre = {k: (e[:1].upper() + e[1:] if e.islower() and len(e) > 6 else e) for k, e in zip(best.k, best.e)}
    return key.map(nombre)


def _categorias(P, maxn=10):
    """P: votos (provincia, unidad) x etiqueta. Nacionales de 3 % o más (hasta 8) y las de 30 % o más en alguna provincia."""
    tot = P.sum()
    tot = tot[[c for c in tot.index if not OTROS_RE.search(ascii_up(c))]]
    share = (tot / P.values.sum()).sort_values(ascending=False)
    keep = list(share[share >= .03].index[:8])
    prov = P.groupby(level=0).sum(); prov = prov.div(prov.sum(1), axis=0)
    fuertes = prov.max().reindex(share.index)
    for c in fuertes[fuertes >= .30].index:
        if c not in keep and len(keep) < maxn: keep.append(c)
    if not keep: keep = list(share.index[:3])
    return keep


def tabla_master(anio, cargo, fuente):
    df = master()
    x = df[(df.anio == anio) & (df.cargo == cargo) & (df.fuente_id == fuente)].copy()
    x["prov"] = x.provincia.map(prov_canon); x["u"] = [nkp(p, n) for p, n in zip(x.prov, x.unidad)]
    x["etq"] = x.bloque.fillna(x.partido).fillna(x.codigo_partido).fillna("Otros").astype(str).str.strip()
    if 1983 <= anio <= 1999 and x.bloque.isna().all():     # base de E. Calvo sin bloque: familia del código según los atlas
        fam = x.codigo_partido.map(lambda c: familia(anio, c))
        x["etq"] = fam.fillna(x.etq)
    x = x[~((x.tipo_fila == "agrupacion") & x.codigo_partido.astype(str).str.fullmatch(r"pos\d*"))]   # 1997: positivos como columna
    key = ["prov", "u"]
    part = x[x.tipo_fila == "agrupacion"].copy()
    part["etq"] = _unificar(part.etq, part.votos.fillna(0))
    cand = x[(x.tipo_fila == "candidato") & ~x.set_index(key).index.isin(part.set_index(key).index)]
    if len(cand):        # 1912/1914: unidades con votos por candidato y no por lista -> el candidato más votado de cada partido
        cand = cand.groupby(key + ["etq"], as_index=False).votos.max()
    part = pd.concat([part[key + ["etq", "votos"]], cand])
    P = part.pivot_table(index=key, columns="etq", values="votos", aggfunc="sum", fill_value=0)
    nombres = x.groupby(key).unidad.first()
    cats = _categorias(P)
    T = pd.DataFrame(index=P.index)
    for c in cats: T[c] = P[c]
    T["Otros"] = P.drop(columns=cats).sum(1)
    met = x[x.tipo_fila != "agrupacion"].pivot_table(index=key, columns="tipo_fila", values="votos", aggfunc="max")
    met = met.reindex(T.index)
    bn = sum(met[t].fillna(0) for t in BN_TIPOS if t in met) if any(t in met for t in BN_TIPOS) else pd.Series(0., T.index)
    pos = T.sum(1)
    for t in ("votantes", "total"):      # sin desglose de blancos y nulos: la diferencia con los votantes
        if t in met:
            bn = bn.where(bn > 0, (met[t] - pos).clip(lower=0).fillna(0))
            break
    T["Blanco y nulo"] = bn
    el = met["electores_mesas_escrutadas"] if "electores_mesas_escrutadas" in met else met["electores"] if "electores" in met else None
    if el is not None:
        nv = el - T.sum(1)
        T["No votó"] = nv.where(nv >= 0)       # NaN: sin electores o padrón inconsistente en esa unidad
    T = T.loc[T.drop(columns=["No votó"], errors="ignore").sum(1) > 0]
    T.attrs["nombres"] = nombres.reindex(T.index).to_dict()
    return T


def _secname(k, d, s, cache={}):
    a = PKL[k][0]
    for y in (a, 2011):
        if y not in cache:
            try: cache[y] = estimar.secnames(y)
            except Exception: cache[y] = {}
        if (d, s) in cache[y]: return cache[y][(d, s)]
    return "SECCION %d" % s


def tabla_pkl(k):
    """El pkl llevado a departamento (sección) con nombre, para cruzarlo con otras fuentes."""
    T, cats = estimar.load(int(k) if k.isdigit() else k)
    names = {}
    idx = []
    for d, s, c in T.index:
        n = c[2:] if str(c).startswith("S:") else (c if s == 0 else _secname(k, d, s))
        idx.append((DISTRITOS.get(d, d), nkp(DISTRITOS.get(d, d), n))); names[idx[-1]] = n
    T = T.copy(); T.index = pd.MultiIndex.from_tuples(idx, names=["prov", "u"])
    T = T.groupby(level=[0, 1]).sum()
    if "No votó" in T: T["No votó"] = T["No votó"].where(T["No votó"] >= 0)
    T.attrs["nombres"] = names
    return T


def _num(s):
    s = re.sub(r"[^\d,]", "", str(s)).split(",")[0]
    return float(s) if s else np.nan


BN_RE = re.compile(r"BLANCO|NULO|ANULAD|IMPUGN|RECURRID|BRONCA")


def tabla_atlas(rel):
    """Unidades de un dataset de atlas (mapas/mapa*/dataset_*.json): líneas por unidad del primer modo.
    Cada línea va al bloque de la leyenda (código igual o mismo color, si es único) o, si no, a su agrupación
    (el nombre antes de « – »). En las PASO presidenciales, por precandidato salvo que se pida «#agrupacion»."""
    import json
    rel, _, opc = rel.partition("#")
    f = os.path.join(ROOT, rel); carpeta = os.path.basename(os.path.dirname(f))
    d = json.load(open(f, encoding="utf8"))
    C = d["candidates"]; m = d["modes"][0]
    blocs = [x["code"] for x in m.get("national", {}).get("cands", []) if x["code"] in C]
    color = {}
    for b in blocs: color.setdefault(C[b].get("base"), []).append(b)
    por_lista = PASO_PRES.match(carpeta) and opc != "agrupacion"

    def etq(code):
        c = C.get(code, {}); n = str(c.get("n", code))
        if BN_RE.search(ascii_up(n)) or re.search(r"_(BLA|NUL)$", code): return "Blanco y nulo"
        if por_lista: return n
        if code in blocs: return C[code]["n"]
        b = color.get(c.get("base"), [])
        if len(b) == 1: return C[b[0]]["n"]
        return n.split(" – ")[0]

    solid = set(d.get("solid") or [])
    filas, vistos = [], set()

    def agregar(p, n, u):
        lines = [(l[0], l[1]) for l in (u or {}).get("lines", []) if isinstance(l[1], (int, float))]
        if not lines: return
        firma = (p, n, tuple(lines)) if d["territories"][0].get("k") == "circuito" else (p, tuple(lines))
        if firma in vistos: return              # la misma unidad dibujada en varios polígonos
        vistos.add(firma)
        met = {a[0]: _num(a[1]) for a in u.get("metrics", [])}
        el = next((met[k] for k in ("Electores (mesas escrutadas)", "Inscriptos", "Electores") if k in met), np.nan)
        vot = met.get("Votantes", np.nan)
        r = dict(prov=prov_canon(p), u=nkp(prov_canon(p), n), nombre=n, _el=el, _vot=vot)
        for code, v in lines:
            k = etq(code); r[k] = r.get(k, 0) + v
        filas.append(r)

    for t, u in zip(d["territories"], m.get("units", [])):
        p, n = t["p"], t["n"]
        if t.get("k") == "circuito":           # AMBA 2025 por circuito: se suma al partido o a la comuna
            p, n = (p, n.split("·")[-1].strip()) if prov_canon(p) == "Ciudad de Buenos Aires" else ("Buenos Aires", p)
        if p not in solid: agregar(p, n, u)
    for p in solid:                            # provincia pintada con su total: una sola unidad
        agregar(p, p + " (provincia entera)", m.get("prov", {}).get(p))
    D = pd.DataFrame(filas)
    nombres = D.groupby(["prov", "u"]).nombre.first()
    D = D.drop(columns="nombre").groupby(["prov", "u"]).sum(min_count=1)
    el, vot = D.pop("_el"), D.pop("_vot")
    P = D.drop(columns=["Blanco y nulo"], errors="ignore").fillna(0)
    cats = _categorias(P, maxn=12 if por_lista else 10)
    T = pd.DataFrame(index=D.index)
    for c in cats: T[c] = P[c]
    T["Otros"] = P.drop(columns=cats).sum(1)
    bn = D["Blanco y nulo"].fillna(0) if "Blanco y nulo" in D else pd.Series(0., D.index)
    bn = bn.where(bn > 0, (vot - T.sum(1)).clip(lower=0).fillna(0))
    T["Blanco y nulo"] = bn
    if el.notna().any():
        nv = el - T.sum(1)
        T["No votó"] = nv.where(nv >= 0)
    T.attrs["nombres"] = nombres.to_dict()
    return T


CORTOS = [(r"^(ALIANZA )?FRENTE DE IZQUIERDA Y DE (LOS )?TRABAJADORES\W*UNIDAD", "FIT-U"),
          (r"^(ALIANZA )?FRENTE DE IZQUIERDA Y DE (LOS )?TRABAJADORES", "FIT")]
MENORES = {"de", "del", "la", "las", "los", "el", "y", "e", "por", "para", "en", "a", "con"}


def corto(n):
    """Etiqueta legible: siglas conocidas y nombres en mayúsculas pasados a tipo título."""
    k = ascii_up(n)
    for pat, rep in CORTOS:
        if re.search(pat, k): return rep
    if n.isupper() and len(n) > 5:
        def palabra(i, x):
            if "." in x or x.startswith("(") or len(x) <= 3 and x.lower() not in MENORES: return x   # siglas
            x = x.lower()
            return x if (i and x in MENORES) else x[:1].upper() + x[1:]
        n = " ".join(palabra(i, x) for i, x in enumerate(re.sub(r"^ALIANZA ", "", n).split()))
    return n


def _renombrar(T):
    nv = T.pop("No votó") if "No votó" in T else None
    attrs = T.attrs
    T = T.T.groupby([corto(c) for c in T.columns], sort=False).sum().T
    T.attrs = attrs
    if nv is not None: T["No votó"] = nv
    return T


def tabla(eid):
    if eid not in _tablas:
        if eid.startswith("a:"):
            T = tabla_atlas(eid[2:])
        elif eid.startswith("pkl:"):
            T = tabla_pkl(eid[4:])
        else:
            a, c, f = eid[2:].split("|")
            T = tabla_master(int(a), c, f)
        _tablas[eid] = _renombrar(T)
    return _tablas[eid]


def emparejar(ua, ub):
    """Unidades de la misma provincia: igual clave normalizada y, para las que quedan, parecido de nombre único (≥ 0,85)."""
    par = {u: u for u in ua if u in ub}
    ra = [u for u in ua if u not in par]; rb = [u for u in ub if u not in par.values()]
    cand = {}
    for u in ra:
        m = difflib.get_close_matches(u, rb, n=2, cutoff=.85)
        if len(m) == 1 or (len(m) == 2 and difflib.SequenceMatcher(None, u, m[0]).ratio() - difflib.SequenceMatcher(None, u, m[1]).ratio() > .05):
            cand[u] = m[0]
    usados = pd.Series(list(cand.values()), dtype=object).value_counts()
    par.update({u: v for u, v in cand.items() if usados[v] == 1})
    return par


def anio(eid):
    if eid.startswith("pkl:"): return PKL[eid[4:]][0]
    if eid.startswith("m:"): return int(eid[2:].split("|")[0])
    import json
    return int(json.load(open(os.path.join(ROOT, eid[2:].partition("#")[0]), encoding="utf8"))["year"])


# --- colores ------------------------------------------------------------------------------------------------
_colores = None
HEUR = [(r"BLANCO Y NULO", "#5b5b5b"), (r"NO VOTO", "#c8c8c8"), (r"^OTROS", "#9e9e9e"),
        (r"LIBERTAD AVANZA|MILEI|LIBERTARIO", "#6c4c98"), (r"FUERZA PATRIA|UNION POR LA PATRIA|MASSA", "#009ce4"),
        (r"FRENTE DE TODOS|UNIDAD CIUDADANA|FERNANDEZ", "#2ea3ff"), (r"VICTORIA|KIRCHNER|SCIOLI", "#50ade6"),
        (r"JUNTOS POR EL CAMBIO|CAMBIEMOS|MACRI|BULLRICH|PROPUESTA REPUBLICANA|\bPRO\b|UNION PRO", "#f4ce00"),
        (r"IZQUIERDA|TRABAJADORES|OBRERO|\bFIT\b|COMUNISTA|\bMAS\b|SOCIALISMO", "#f65058"),
        (r"HACEMOS|SCHIARETTI|CONSENSO FEDERAL|LAVAGNA|TERCERA VIA", "#283084"),
        (r"PROVINCIAS UNIDAS", "#FF682C"), (r"RENOVADOR|UNA\b|UNIDOS POR UNA NUEVA", "#231f20"),
        (r"FREPASO|FRENTE GRANDE|PAIS SOLIDARIO|BORDON", "#a349a4"), (r"ALIANZA$|ALIANZA PARA EL TRABAJO|DE LA RUA", "#dc0143"),
        (r"ACCION POR LA REPUBLICA|CAVALLO", "#3e5298"), (r"UCEDE|CENTRO DEMOCRATICO|ALIANZA DE CENTRO|ALSOGARAY", "#8e6bd8"),
        (r"INTRANSIGENTE|UCRI|FRONDIZI", "#f4845f"), (r"RADICAL|\bUCR\b|ALFONSIN|ANGELOZ|BALBIN|YRIGOYEN|ALVEAR|ILLIA|MASSACCESI|TAMBORINI", "#e10019"),
        (r"JUSTICIALIST|PERON|\bPJ\b|FREJULI|FREJUPO|MENEM|LUDER|DUHALDE|CAMPORA|UNION POPULAR|LABORISTA", "#318ce7"),
        (r"SOCIALISTA|PROGRESISTA|BINNER|STOLBIZER|JUSTO\b|REPETTO|BRAVO", "#ff9900"),
        (r"DEMOCRATA PROGRESISTA|DE LA TORRE", "#005c9e"), (r"CONSERVADOR|DEMOCRATA NACIONAL|CONCORDANCIA|CONCENTRACION|UNION NACIONAL|MANRIQUE", "#30d5c8"),
        (r"COALICION CIVICA|\bARI\b|CARRIO|AFIRMACION PARA UNA", "#74b744"), (r"MODIN|RICO\b", "#e67e22"),
        (r"MOVIMIENTO POPULAR NEUQUINO|NEUQUIN", "#14306e"), (r"FUERZA REPUBLICANA|BUSSI", "#7b3f00"),
        (r"BLOQUISTA", "#44944a"), (r"AUTONOMISTA|LIBERAL", "#40e0d0"), (r"RODRIGUEZ SAA|COMPROMISO FEDERAL|PERONISMO FEDERAL", "#1aff98")]
PALETA = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#1f78b4", "#b15928", "#6a3d9a", "#33a02c", "#fb9a99"]


def _mapa_colores():
    import json
    import sankey
    col = {ascii_up(k): v for k, v in sankey.COL.items()}
    for f in _atlas_files():
        d = json.load(open(f, encoding="utf8")); C = d["candidates"]
        for x in d["modes"][0].get("national", {}).get("cands", []):
            c = C.get(x["code"], {})
            if c.get("n") and c.get("base"): col.setdefault(ascii_up(c["n"]), c["base"])
    return col


def colores(nombres):
    global _colores
    if _colores is None: _colores = _mapa_colores()
    out, usados = {}, set()
    for n in nombres:
        k = ascii_up(n)
        c = _colores.get(k) or next((v for pat, v in HEUR if re.search(pat, k)), None)
        if c is None:
            c = PALETA[sum(map(ord, n)) % len(PALETA)]
        out[n] = c
    return out
