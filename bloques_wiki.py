"""Bloques de logo de los mapas presidenciales de la Wikipedia, para las legislativas 2003-2025.

Los mapas «Elecciones presidenciales de Argentina de <año> - Resultados.png» de Commons (CC0, usuario N2051)
llevan en la leyenda una versión de cada logo pensada para su barra (VICTORIA en su recuadro blanco, las franjas
de Cambiemos, TODOS en blanco, el león de LLA...). Se recortaron de los originales en alta resolución con la
barra vuelta transparente (`logos_wikipedia/bloques_presidenciales/`, ver LICENCIAS.md) y se usan, elegidos caso
por caso, para el mismo partido en la legislativa más cercana. La leyenda los dibuja llenando el bloque del logo.
"""
import os, io, base64

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos_wikipedia", "bloques_presidenciales")

# (años, fragmento del nombre en la leyenda, bloque)
BLOQUES = [
    ((2003,), "recrear", "recrear"),
    ((2003,), "afirmación para una república", "ari"),
    ((2005, 2007, 2009), "frente para la victoria", "fpv07"),
    ((2011, 2013), "frente para la victoria", "fpv11"),
    ((2015,), "frente para la victoria", "fpv15"),
    ((2007,), "coalición cívica", "cc"),
    ((2007,), "nación avanzada", "una07"),
    ((2011,), "frente amplio progresista", "fap"),
    ((2011,), "desarrollo social", "udeso"),
    ((2011,), "frente popular", "fp11"),
    ((2011, 2013), "compromiso federal", "cf11"),
    ((2015,), "compromiso federal", "cf15"),
    ((2015, 2017), "cambiemos", "cambiemos"),
    ((2015,), "nueva alternativa", "una15"),
    ((2019, 2021), "frente de todos", "fdt"),
    ((2019,), "juntos por el cambio", "sisepuede"),
    ((2021, 2023), "juntos por el cambio", "jxc23"),
    ((2019,), "consenso federal", "consenso"),
    ((2021,), "tercera vía", "hacemos"),
    ((2023,), "hacemos por nuestro país", "hacemos"),
    ((2023,), "unión por la patria", "up"),
    ((2023, 2025), "libertad avanza", "lla"),
]


def aplicar(CAND, year):
    """Reemplaza el logo de los partidos con bloque de la Wikipedia. Devuelve [(código, bloque)]."""
    from PIL import Image
    usados = []
    for code, c in CAND.items():
        n = (c.get("n") or "").lower()
        for years, frag, blk in BLOQUES:
            if year in years and frag in n:
                im = Image.open(os.path.join(DIR, blk + ".png")).convert("RGBA")
                b = io.BytesIO(); im.save(b, "PNG", optimize=True)
                c.update(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(),
                         ar=round(im.width / im.height, 4), blk=blk)
                usados.append((code, blk))
                break
    return usados
