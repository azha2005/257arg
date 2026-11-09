# -*- coding: utf-8 -*-
"""Mapa del cuadro del 17 de mayo de 1874. Columnas Alsina–Avellaneda y Mitre."""
from html import escape
from pathlib import Path
import json
import unicodedata

import geopandas as gpd

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[1]
CIUDAD = """
San Miguel|109|172
San Nicolás|168|234
Balvanera|||Nula
San Telmo|166|363
Monserrat|273|284
San Juan Evangelista|31|111
Catedral al Norte|96|246
Concepción|393|165
Socorro|180|185
Santa Lucía|9|177
Catedral al Sur|102|254
San Cristóbal|250|157|Modificada
Pilar|118|117
Piedad|300|268
"""
CAMPAÑA = """
Pilar|103|93
Morón|113|20
Bahía Blanca|20|44
Ayacucho|120|32
San Pedro|24|304
Dolores|62|115
Pila|0|366|Nada para Alsina–Avellaneda
Baradero|82|198
Ramallo|61|203
Mercedes|244|191
San Nicolás|462|422
Vecino|0|339|Nada para Alsina–Avellaneda. Otra fila: 339 alsinistas, marcada falsificada
Zárate|82|120
Tuyú||661|Otra fila: 710 alsinistas, marcada falsificada
General Alvear|79|27
Magdalena|32|378
Mar Chiquita|0|79|Nada para Alsina–Avellaneda
Juárez|0|290|Nada para Alsina–Avellaneda. Otra fila: 356 alsinistas, marcada falsificada
Nueve de Julio|3|125
Suipacha|85|50
Chacabuco|757||Falsificada
Monte|467|446
25 de Mayo|302|263
Bragado|319|281
Carmen de Areco|122|94
Rauch|259|40
Monsalvo|0|436|Nada para Alsina–Avellaneda. Otra fila: 607 alsinistas, marcada falsificada
Arrecifes|271|206
Necochea|272||No hubo elección
San Andrés de Giles||234|Otra fila: 386 alsinistas, marcada falsificada
Las Conchas|87|80
La Matanza|6|114
Tapalqué||89
Tandil|22|285
Lobos|0|72|Nada para Alsina–Avellaneda
Lomas de Zamora|34|49
Chascomús|189|
Ranchos|54|202
Cañuelas||260
Lincoln||77
Saladillo|211|134
Merlo|106|7
Lobería||293
Castelli|18|103
General Lavalle|13|84
Pergamino||811
Las Heras|102|57
Moreno||69
Tordillo||97
Las Flores|58|119
Barracas al Sud|52|84
Rojas|172|137
San Isidro|127|142
San Antonio de Areco|59|67
Salto|186|296
Belgrano|99|27
Navarro||431
Exaltación de la Cruz|98|76
Ensenada||38
Chivilcoy|201|579
Balcarce|2|59
Azul|74|210
Luján|109|34
San Fernando|79|85
San Vicente|59|85
San José de Flores|120|114
Tres Arroyos|1|37
Junín|72|50
Quilmes|94|126
"""

def clave(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if not unicodedata.combining(c))

def filas(tabla):
    return {clave(n): (a, m, nota[0] if nota else "")
            for n, a, m, *nota in (linea.split("|") for linea in tabla.strip().splitlines())}

def unidad(nombre, d, fila):
    color, detalle = "#c3b89f", "Sin dato en el recorte"
    if fila:
        a, m, nota = fila
        detalle = f"Alsina–Avellaneda {a or '—'} · Mitre {m or '—'}"
        if nota:
            detalle += " · " + nota
        if nota in {"Nula", "Falsificada", "No hubo elección"}:
            color = "#83838a"
        elif a and m:
            diferencia = int(m) - int(a)
            color = "#4169c1" if diferencia > 0 else "#b44945" if diferencia < 0 else "#83838a"
            detalle += f" · Margen {abs(diferencia)}"
            if int(m) + int(a):
                detalle += f" · Mitre {int(m)/(int(m)+int(a)):.1%}".replace(".", ",")
        elif a or m:
            color = "#7594cf" if m else "#cf807d"
            detalle += " · Una cifra publicada"
    etiqueta = escape(f"{nombre} · {detalle}", quote=True)
    return f'<path d="{d}" fill="{color}" tabindex="0" data-ficha="{etiqueta}"><title>{etiqueta}</title></path>'

base = json.loads((ROOT / "mapas/capital_canton/geometria.json").read_text(encoding="utf-8"))
ciudad = filas(CIUDAD)
assert set(ciudad) == {clave(n) for n in base["p1872"]}
urbano = [unidad(n.title(), v["d"], ciudad[clave(n)]) for n, v in base["p1872"].items()]
nombres = {clave(linea.split("|")[0]): linea.split("|")[0] for linea in CIUDAD.strip().splitlines()}
abreviados = {"catedral al norte": "Cat. Norte", "catedral al sur": "Cat. Sur",
              "san juan evangelista": "San Juan Ev."}
etiquetas = []
for n, unidad_geo in base["p1872"].items():
    x, y = unidad_geo["c"]
    nombre = abreviados.get(clave(n), nombres[clave(n)])
    etiquetas.append(f'<text x="{x}" y="{y}">{escape(nombre)}</text>')
shp = ROOT / "geometria/Base deptos 1869-2022/Departamentos_1869.shp"
geo = gpd.read_file(shp)
geo = geo.loc[geo.PROV_COD == "06"].to_crs(32721)
x0, y0, x1, y1 = geo.total_bounds
factor = 850 / (y1 - y0)

def path(g):
    g = g.simplify(450, preserve_topology=True)
    partes = [g] if g.geom_type == "Polygon" else g.geoms
    return "".join("M" + "L".join(f"{(x-x0)*factor:.2f},{(y1-y)*factor:.2f}" for x,y in r.coords) + "Z"
                   for p in partes for r in [p.exterior, *p.interiors])

campo = filas(CAMPAÑA)
rural = [unidad(r.DEPTO, path(r.geometry), campo.get(clave(r.DEPTO))) for r in geo.itertuples()]
faltan = [n for n in campo if n not in {clave(v) for v in geo.DEPTO}]
html = f"""<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Buenos Aires · Presidencial de 1874</title>
<style>
body{{margin:24px;background:#101112;color:#eee;font:17px system-ui}} h1{{font-size:clamp(26px,5vw,58px);margin:0}} h1 em{{color:#58bbb3;font-style:normal}}
main{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} section{{min-width:0;background:#191b1c;padding:14px}} svg{{width:100%;height:min(63vh,620px)}}
path{{stroke:#151617;stroke-width:1;fill-rule:evenodd;vector-effect:non-scaling-stroke;cursor:pointer}}path:is(:hover,:focus){{stroke:white;stroke-width:2;outline:none}}
.etiquetas1874{{pointer-events:none;fill:white;stroke:#101112;stroke-width:2px;paint-order:stroke;text-anchor:middle;dominant-baseline:middle;font-size:10px;font-weight:600}}
#ficha{{padding:12px;background:#252829}}small{{color:#ccc}} @media(max-width:650px){{main{{grid-template-columns:1fr}}}}
</style>
<h1>Buenos Aires, <em>1874</em> · Presidente</h1>
<p>12 de abril · Elección de electores · Cuadro publicado el 17 de mayo</p>
<p><span style="color:#7594cf">■ Mitre</span> · <span style="color:#cf807d">■ Alsina–Avellaneda</span> · Gris: resultado objetado o sin elección · Beige: sin datos. Tono claro: una cifra publicada.</p>
<p id="ficha" aria-live="polite">Pasá el cursor o tocá un partido o parroquia para ver la ficha.</p>
<main><section><h2>Campaña bonaerense</h2><svg viewBox="-8 -8 {(x1-x0)*factor+16:.2f} 866">{''.join(rural)}</svg></section>
<section><h2>Ciudad de Buenos Aires</h2><svg viewBox="{' '.join(map(str,base['p1872_vista']))}">{''.join(urbano)}<g class="etiquetas1874" aria-hidden="true">{''.join(etiquetas)}</g></svg></section></main>
<p>Total impreso del cuadro: Mitre 14.971 · Alsina–Avellaneda 12.103 · Diferencia 2.868. Se conserva como cifra de la fuente, sin ajustar las filas.</p>
<p><small>Fuente: recortes aportados del 17 de mayo. Los guiones se conservan como cifra ausente. «Nada» se muestra como cero con nota. Las cifras de las filas objetadas se reproducen con su marca. Los porcentajes usan los votos de ambos bandos en las filas con dos cifras.</small></p>
<p><small>Geometría de Rodríguez y De Grande, SHP de 1869. Se usa como aproximación para 1874. Ciudad: reconstrucción parroquial del visor Capital. Filas sin correspondencia directa en el SHP: {escape(', '.join(n.title() for n in faltan))}. General Alvear: 79–27. General Lavalle: 13–84. Lomas de Zamora: 34–49.</small></p>
<script>document.querySelectorAll('[data-ficha]').forEach(p=>{{for(const evento of ['mouseenter','focus','click'])p.addEventListener(evento,()=>document.getElementById('ficha').textContent=p.dataset.ficha)}})</script>
"""
(DIR / "atlas_1874pres.html").write_text(html, encoding="utf-8")
print(len(urbano),len(rural),len(campo)-len(faltan),faltan)
