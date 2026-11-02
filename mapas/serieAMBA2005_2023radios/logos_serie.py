"""Reemplazos por contenido: alcanzan diputados, presidenciales y PASO.

Los recortes viejos no se modifican: otros atlas conservan sus propios recursos.
"""
import base64
import hashlib
import io
from PIL import Image
from serie import ROOT


def corregir(candidates):
    def signature(raw):
        image = Image.open(io.BytesIO(raw)).convert('RGBA')
        return (image.size, hashlib.sha256(image.tobytes()).hexdigest())

    replacements = {}
    for old, new in [
        ('cc.png', 'datos/fuentes_leg2003_2025/logos/Coalición_Cívica_(recortado).png'),
        ('una07.png', 'datos/fuentes_leg2003_2025/logos/Concertación_para_una_Nación_Avanzada.png'),
        ('fap.png', 'datos/fuentes_leg2003_2025/logos/Frente_Amplio_Progresista.gif'),
        ('cambiemos.png', 'logos/bloques_presidenciales/cambiemos_franja_completa.png'),
        ('sisepuede.png', 'logos/bloques_presidenciales/sisepuede_franja_completa.png'),
        ('jxc23.png', 'logos/bloques_presidenciales/jxc23_franja_completa.png'),
        ('lla.png', 'logos/Logo_La_Libertad_Avanza_sin_aguila_blanco.svg'),
        ('up.png', 'datos/fuentes_leg2003_2025/logos/Logo_Union_por_la_Patria.svg'),
    ]:
        raw = (ROOT / 'logos/bloques_presidenciales' / old).read_bytes()
        replacements[signature(raw)] = new
    changes = []
    for code, c in candidates.items():
        if not c.get('img'): continue
        raw = base64.b64decode(c['img'].split(',', 1)[1])
        target = replacements.get(signature(raw))
        if target:
            if target.endswith('.svg'):
                import resvg_py
                im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_path=str(ROOT / target),height=280)))).convert('RGBA')
                if target.endswith('Logo_Union_por_la_Patria.svg'):
                    # Símbolo completo anterior al espacio que lo separa del nombre.
                    occupied = [x for x in range(im.width) if im.getchannel('A').crop((x,0,x+1,im.height)).getbbox()]
                    end = next(a+1 for a,b in zip(occupied,occupied[1:]) if b-a>=8)
                    im = im.crop((0,0,end,im.height))
            else:
                im = Image.open(ROOT / target).convert('RGBA')
            if target.endswith('.svg'):
                bounds = im.getbbox()
                if bounds: im = im.crop(bounds)
            buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
            c.update(img='data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(),
                     logo_file=target)
            c.pop('blk', None)
            changes.append(dict(codigo=code, archivo=target))
        else:
            im = Image.open(io.BytesIO(raw))
        # La relación de aspecto se obtiene del archivo, no de un atlas heredado.
        c['ar'] = im.width / im.height
    return changes
