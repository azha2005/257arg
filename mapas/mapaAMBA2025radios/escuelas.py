"""Empareja los locales de votacion con los padrones oficiales de escuelas con coordenadas (como LN Data / Poblaciones).
PBA: establecimientos-educativos-26102026.geojson (Direccion General de Cultura y Educacion, catalogo.datos.gba.gob.ar).
CABA: establecimientos_educativos_WGS84.geojson (Ministerio de Educacion GCBA, data.buenosaires.gob.ar).
Dentro del mismo partido (comuna en Capital), por:
  dir    = misma calle (alguna palabra en comun) y altura a menos de 30;
  codigo = mismo tipo y numero de escuela (EP 39, ES 25, EST 3, JI 912, EE 531), solo PBA;
  nombre = nombre muy parecido (colegios privados), unico en el partido.
"""
import os, re, json, difflib, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PBA = os.path.join(ROOT, "datos", "escuelas", "pba", "establecimientos-educativos-26102026.geojson")
CABA = os.path.join(ROOT, "datos", "escuelas", "caba", "establecimientos_educativos_WGS84.geojson")


def nn(s):
    s = unicodedata.normalize("NFD", str(s or "").upper().replace("�", "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", s)).strip()


def muni(s):
    s = nn(s).replace("GRAL ", "GENERAL ").replace("JOSE C PAZ", "JOSE CLEMENTE PAZ")
    return s.replace(" ", "")


STOP = set("AV AVDA AVENIDA CALLE GRAL GENERAL DR DRA ING PTE PRESIDENTE CNEL CORONEL TTE TENIENTE DE DEL LA LAS LOS EL Y ENTRE E BIS DIAG "
           "PJE PASAJE RUTA S N NRO NO SAN SANTA STA PROF PADRE PBRO BRIG CMDTE ALTE ALMIRANTE MAYOR SGTO CAP CAPITAN ESQ ESQUINA KM SN".split())


def addr_parts(s, school_pba=False):
    """(palabras de la calle, altura)"""
    t = str(s or "")
    if school_pba and " - " in t:
        st, _, no = t.rpartition(" - ")
    else:
        t2 = re.split(r"\bENTRE\b(?!\s+RIOS)|\bE/", t.upper())[0]
        m = re.search(r"N\s*\W?\s*(\d+)", t2)
        if m and re.search(r"\bN\s*[\W\d]", t2): st, no = t2[:m.start()], m.group(1)
        else:
            m = re.search(r"(\d+)\s*\D{0,3}$", t2)
            st, no = (t2[:m.start()], m.group(1)) if m else (t2, "")
    st = re.split(r"\bENTRE\b(?!\s+RIOS)|\bE/|\bY\b", nn(st))[0] if school_pba else nn(st)
    words = {w for w in st.split() if (len(w) >= 3 or w.isdigit()) and w not in STOP}
    no = re.sub(r"\D", "", no)
    return words, int(no) if no else None


def codes_voto(s):
    t = nn(s)
    out = set()
    for pat, c in ((r"\bEST N ?(\d+)", "EST"), (r"\bEP N ?(\d+)", "EP"), (r"\bES N ?(\d+)", "ES"), (r"\bEES N ?(\d+)", "ES"), (r"\bEEST N ?(\d+)", "EST"),
                   (r"JARDIN DE INFANTES N ?(\d+)", "JI"), (r"\bJI N ?(\d+)", "JI"), (r"ESPECIAL N ?(\d+)", "EE"), (r"\bEEE N ?(\d+)", "EE"),
                   (r"\bEPB N ?(\d+)", "EP"), (r"\bESB N ?(\d+)", "ES"), (r"\bEET N ?(\d+)", "EST"), (r"\bEEM N ?(\d+)", "ES")):
        for m in re.finditer(pat, t): out.add((c, int(m.group(1))))
    # «ESCUELA EP N°31/ES N°25»: el segundo codigo viene despues de la barra
    return out


def code_escuela(tipo, nro):
    t = nn(tipo)
    if not nro: return None
    if "ADULTOS" in t: return None
    if "SECUNDARIA TECNICA" in t: c = "EST"
    elif "PRIMARIA" in t: c = "EP"
    elif "SECUNDARIA" in t or "EDUCACION MEDIA" in t: c = "ES"
    elif "JARDIN DE INFANTES" in t: c = "JI"
    elif "ESPECIAL" in t: c = "EE"
    else: return None
    return (c, int(nro))


def load():
    S = {}
    for f in json.load(open(PBA, encoding="utf8"))["features"]:
        p = f["properties"]; g = f["geometry"]
        if not g: continue
        w, no = addr_parts(p["direccion"], school_pba=True)
        S.setdefault(("02", muni(p["municipio_nombre"])), []).append(dict(n=nn(p["establecimiento_nombre"]), w=w, no=no, c=code_escuela(p["tipo_organizacion"], p["nro_escuela"]),
                                                                       xy=tuple(g["coordinates"][:2])))
    for f in json.load(open(CABA, encoding="utf8"))["features"]:
        p = f["properties"]; g = f["geometry"]
        if not g or not p.get("COMUNA"): continue
        for dom in {p.get("DOM_ESTABL"), p.get("DOM_EDIFIC")}:
            if not dom: continue
            w, no = addr_parts(dom)
            S.setdefault(("01", "COMUNA%d" % int(p["COMUNA"])), []).append(dict(n=nn(p["NOMBRE_EST"]), w=w, no=no, c=None, xy=tuple(g["coordinates"][:2])))
    return S


def spread(pts):
    import math
    if len(pts) < 2: return 0
    return max(math.dist(a, b) for a in pts for b in pts) * 100000


def match(dist, seccion_nombre, nombre, direccion, S):
    """devuelve (metodo, lon, lat) o None"""
    cand = S.get((dist, muni(seccion_nombre)), [])
    if not cand: return None
    w, no = addr_parts(direccion)
    if no:
        hit = [s for s in cand if s["no"] and abs(s["no"] - no) <= 30 and (w & s["w"])]
        if hit:
            hit.sort(key=lambda s: (abs(s["no"] - no), -len(w & s["w"])))
            return ("escuela_dir", *hit[0]["xy"])
    cs = codes_voto(nombre)
    if cs:
        hit = [s for s in cand if s["c"] in cs]
        if hit and spread([s["xy"] for s in hit]) < 300:
            return ("escuela_codigo", *hit[0]["xy"])
        # varias escuelas con el mismo codigo (sedes, anexos): la de calle en comun
        hit2 = [s for s in hit if w & s["w"]]
        if hit2 and spread([s["xy"] for s in hit2]) < 300:
            return ("escuela_codigo", *hit2[0]["xy"])
    nm = nn(nombre)
    sc = sorted(((difflib.SequenceMatcher(None, nm, s["n"]).ratio(), i) for i, s in enumerate(cand)), reverse=True)[:2]
    if sc and sc[0][0] >= 0.85 and (len(sc) < 2 or sc[1][0] < 0.85 or spread([cand[sc[0][1]]["xy"], cand[sc[1][1]]["xy"]]) < 300):
        return ("escuela_nombre", *cand[sc[0][1]]["xy"])
    return None
