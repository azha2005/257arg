"""Calco de la lámina municipal para las 17 parroquias electorales de marzo de 1896."""
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator, RBFInterpolator
from shapely import get_parts, make_valid, LineString, Point, Polygon, polygonize, segmentize, set_precision, union_all
from shapely.ops import split, substring, transform

DIR = Path(__file__).parent
FUENTE = json.loads((DIR / "canton1895.json").read_text(encoding="utf-8"))
PLANO = json.loads((DIR / "trazo_municipal1895.json").read_text(encoding="utf-8"))
LIMITES = json.loads((DIR / "limites_lamina1895.json").read_text(encoding="utf-8"))
GRILLA = 0.0001


def _ribera():
    puntos = PLANO["riachuelo"].copy()
    # Empalme de la línea Santa Lucía / San Juan Evangelista con la ribera.
    puntos.insert(puntos.index([713, 552]) + 1, [715, 551])
    puntos = np.array(puntos)
    dist = np.r_[0, np.linalg.norm(np.diff(puntos, axis=0), axis=1).cumsum()]
    muestras = np.union1d(dist, np.arange(0, dist[-1], 3))
    xy = PchipInterpolator(dist, puntos, axis=0)(muestras)
    xy[np.searchsorted(muestras, dist)] = puntos
    return xy.tolist()


def _caras():
    """Cierra las caras a partir de líneas compartidas en píxeles de la lámina."""
    costa = LIMITES["contorno_sin_riachuelo"]
    ribera = _ribera()
    contorno = Polygon(costa + ribera[1:-1])
    red = [LineString(contorno.exterior), LineString(PLANO["san_bernardo"] + PLANO["san_bernardo"][:1])]
    red.extend(LineString(linea) for linea in LIMITES["limites"].values())
    caras = list(polygonize(list(union_all(red).geoms)).geoms)
    etiquetas = {nombre: Point(xy) for nombre, xy in LIMITES["interiores"].items()}
    salida = {}
    for cara in caras:
        nombres = [nombre for nombre, punto in etiquetas.items() if cara.contains(punto)]
        if len(nombres) != 1:
            raise ValueError(f"Cara sin identificación única en {cara.bounds}: {nombres}")
        salida[nombres[0]] = cara
    if set(salida) != set(FUENTE["poblacion"]) | {"DIQUES"}:
        raise ValueError("El calco debe producir 17 parroquias electorales y la franja portuaria")
    return salida, contorno


def _registro():
    registro = np.array(PLANO["registro"])
    return RBFInterpolator(registro[:, 0], registro[:, 1], kernel="thin_plate_spline")


def _proyectar_poligono(geometria, ajustar):
    anillo = segmentize(geometria.exterior, 6)
    return set_precision(Polygon(ajustar(np.array(anillo.coords))), GRILLA)


def _validar(parroquias, contorno):
    conjunto = union_all(list(parroquias.values()), grid_size=GRILLA)
    invalidas = [u for u, g in parroquias.items()
                 if not isinstance(g, Polygon) or not g.is_valid or g.interiors]
    if invalidas:
        raise ValueError(f"Parroquias inválidas, discontinuas o con enclaves: {invalidas}")
    if conjunto.symmetric_difference(contorno).area > 1 or sum(g.area for g in parroquias.values()) - conjunto.area > 1:
        raise ValueError("El calco tiene huecos o solapes")


def reconstruir(secciones, proyectar):
    """Ajusta el calco a la proyección del visor y mide el cruce con el SHP."""
    caras, contorno = _caras()
    ajustar = _registro()
    parroquias = {u: _proyectar_poligono(cara, ajustar) for u, cara in caras.items()}
    contorno = _proyectar_poligono(contorno, ajustar)
    _validar(parroquias, contorno)
    control = {}
    for s, seccion in secciones.items():
        base = transform(proyectar, seccion)
        control[s] = {}
        for u, g in parroquias.items():
            porcentaje = round(100 * base.intersection(g).area / base.area, 3)
            if porcentaje:
                control[s][u] = porcentaje
    return parroquias, control, contorno


def _solo_superficie(g):
    return union_all([p for p in get_parts(g) if p.area], grid_size=GRILLA)


def _agregar(caras, parroquia, pieza):
    caras[parroquia] = union_all([caras[parroquia], _solo_superficie(pieza)], grid_size=GRILLA)


def _dividir(caras, ajustar, origen, destino, linea, punto):
    """Añade un límite a la lámina y asigna el lado que contiene el rótulo."""
    linea = segmentize(LineString(linea), 6)
    partes = list(split(caras[origen], LineString(ajustar(np.array(linea.coords)))).geoms)
    interior = Point(ajustar([punto])[0])
    lado = [p for p in partes if p.contains(interior)]
    if len(lado) != 1 or len(partes) != 2:
        raise ValueError(f"No se pudo reconstruir la división de {origen} para {destino}")
    caras[destino] = set_precision(lado[0], GRILLA)
    caras[origen] = set_precision(next(p for p in partes if p is not lado[0]), GRILLA)


def _eleccion_1898(parroquias):
    caras = dict(parroquias)
    ajustar = _registro()
    # Carmen, Vélez Sársfield y San Carlos se distinguen en la lámina.
    _dividir(caras, ajustar, "BELGRANO", "DEL CARMEN",
             [(225, 48), (248, 109), (308, 105), (356, 131), (375, 146),
              (366, 154), (383, 183), (370, 185), (405, 221), (425, 252)],
             (262, 202))
    _dividir(caras, ajustar, "FLORES", "VELEZ SARSFIELD",
             [(180, 625), (223, 584), (250, 559), (276, 554), (301, 538),
              (341, 497), (297, 450), (325, 441), (313, 401), (307, 366), (320, 311), (322, 272)],
             (220, 430))
    _dividir(caras, ajustar, "FLORES", "SAN CARLOS",
             [(429, 358), (436, 400), (439, 435), (455, 456), (475, 459),
              (477, 502), (516, 547), (541, 575)], (503, 438))
    # Rivadavia (decreto del 16 de junio de 1896) y Gallo (19 de junio).
    _dividir(caras, ajustar, "BALVANERA", "BALVANERA SUR",
             [(503, 373), (562, 367), (647, 365)], (586, 388))
    caras["BALVANERA NORTE"] = caras.pop("BALVANERA")
    _dividir(caras, ajustar, "PILAR", "LAS HERAS",
             [(553, 341), (563, 316), (584, 273), (608, 224), (619, 201)], (554, 258))
    return caras


def _antes_de_san_bernardo(parroquias, secciones):
    caras = dict(parroquias)
    resto = caras.pop("SAN BERNARDO")
    # Cantón y Jorrat cruzan San Bernardo con estas secciones policiales.
    # Su posición se usa para aproximar los territorios anteriores a la parroquia.
    grupos = {"BELGRANO": ("22", "23"), "PILAR": ("17", "21"),
              "BALVANERA": ("09", "11", "28"), "FLORES": ("24", "25", "26")}
    for destino, ids in grupos.items():
        pieza = resto.intersection(union_all([secciones[i] for i in ids], grid_size=GRILLA))
        _agregar(caras, destino, pieza)
        resto = resto.difference(pieza)
    if resto.area:
        _agregar(caras, "FLORES", resto)
    return caras


def _ciudad_antigua(caras, contorno, municipio):
    """Recorta el calco por el límite municipal occidental anterior a 1887."""
    anillo = LineString(municipio.exterior)
    extremo_norte = anillo.project(Point(448, 160))
    extremo_sur = anillo.project(Point(444, 620))
    bajo, alto = sorted([extremo_norte, extremo_sur])
    arcos = [list(substring(anillo, bajo, alto).coords),
             list(substring(anillo, alto, anillo.length).coords)[:-1] + list(substring(anillo, 0, bajo).coords)]
    oeste = min(arcos, key=lambda arco: min(x for x, _ in arco))
    if oeste[0][1] > oeste[-1][1]:
        oeste.reverse()
    corte = Polygon([(oeste[0][0], 90), *oeste, (oeste[-1][0], 700), (760, 700), (760, 90)])
    recorte = set_precision(contorno.intersection(corte).difference(caras["DIQUES"]), GRILLA)
    # El empalme del límite occidental con la ribera de otra fecha deja
    # un fragmento suelto al sur. Se conserva el recinto municipal continuo.
    recorte = max(get_parts(recorte), key=lambda p: p.area)
    salida = {u: _solo_superficie(g.intersection(recorte)) for u, g in caras.items()}
    salida = {u: g for u, g in salida.items() if g.area}
    extension = salida.pop("FLORES")
    al_norte = Polygon([(280, 0), (600, 0), (600, 410), (280, 415)])
    _agregar(salida, "BALVANERA", extension.intersection(al_norte))
    _agregar(salida, "SAN CRISTOBAL", extension.difference(al_norte))
    return salida, recorte


def mayor_pieza(g):
    g = make_valid(g).buffer(0)
    return max(get_parts(g), key=lambda q: q.area)


def contornos_base(municipio1869, secciones1895, proyectar):
    """Contorno de la base de Rodríguez y De Grande para cada versión parroquial,
    en la proyección del visor: 1869 hasta 1886, 1895 desde la anexión."""
    antiguo = set_precision(mayor_pieza(transform(proyectar, municipio1869)), GRILLA)
    nuevo = set_precision(mayor_pieza(transform(proyectar, union_all(list(secciones1895)))), GRILLA)
    return {"p1864": antiguo, "p1872": antiguo, "p1890": nuevo, "p1896": nuevo, "p1898": nuevo}


def ajustar_a_base(caras, base, grilla=GRILLA):
    """Trazo «base»: recorta las parroquias al contorno de la base de Rodríguez y
    De Grande y reparte los huecos (sobre todo la franja costera) y los pedazos
    sueltos entre las vecinas con más superficie de contacto. Los límites
    interiores no cambian. La franja portuaria puede quedar en varias piezas."""
    caras = {u: g.intersection(base) for u, g in caras.items()}
    caras = {u: g for u, g in caras.items() if g.area}
    hueco = base.difference(union_all(list(caras.values())))
    eps = grilla * 10

    def vecina(pieza, excluir=None):
        borde = pieza.buffer(eps)
        return max((v for v in caras if v != excluir), key=lambda v: caras[v].intersection(borde).area)

    for pieza in get_parts(hueco):
        if pieza.area:
            destino = vecina(pieza)
            caras[destino] = union_all([caras[destino], pieza])
    caras = {u: set_precision(make_valid(g).buffer(0), grilla) for u, g in caras.items()}
    for u in [u for u in caras if u != "DIQUES"]:
        partes = sorted(get_parts(caras[u]), key=lambda q: -q.area)
        if len(partes) == 1:
            continue
        caras[u] = partes[0]
        for pieza in partes[1:]:
            destino = vecina(pieza, excluir=u)
            caras[destino] = set_precision(union_all([caras[destino], pieza]).buffer(0), grilla)
    return caras


def variantes(parroquias, contorno, municipio, secciones, proyectar):
    secciones = {s: set_precision(transform(proyectar, g), GRILLA) for s, g in secciones.items()}
    p1890 = _antes_de_san_bernardo(parroquias, secciones)
    p1872, contorno_antiguo = _ciudad_antigua(p1890, contorno, transform(proyectar, municipio))
    p1864 = dict(p1872)
    p1864["BARRACAS AL NORTE"] = p1864.pop("SANTA LUCIA")
    _agregar(p1864, "BARRACAS AL NORTE", p1864.pop("SAN JUAN EVANGELISTA"))
    _agregar(p1864, "BALVANERA", p1864.pop("SAN CRISTOBAL"))
    mapas = {"p1864": (p1864, contorno_antiguo), "p1872": (p1872, contorno_antiguo),
             "p1890": (p1890, contorno), "p1896": (parroquias, contorno),
             "p1898": (_eleccion_1898(parroquias), contorno)}
    for etapa, (caras, limite) in mapas.items():
        try:
            _validar(caras, limite)
        except ValueError as exc:
            raise ValueError(f"{etapa}: {exc}") from exc
    return mapas
