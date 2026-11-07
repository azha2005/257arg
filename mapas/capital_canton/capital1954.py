"""Capital 1954: votos publicados y correspondencia cartográfica provisional.

La numeración adoptada por el usuario es una hipótesis de identificación,
no una transcripción de una delimitación legal.
"""
from pathlib import Path
import hashlib
import json
import re

from shapely.geometry import shape
def _clean(text):
    return re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', text).strip()

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'geometria/circunscripciones1954_caba'
MAPEO = GEO / 'numeracion_adoptada.json'
FUENTE = ROOT / 'transcripciones/peronismo/wiki/w1954.txt'
NOTE = ('Capital 1954: límites interiores aproximados digitalizados de un esquema histórico, '
        'con costa del SHP. Numeración provisional adoptada para este ensayo: nueve lecturas '
        'del usuario sobre la lámina de Derecho UBA; T6=6, T8=8 y T9=9 inferidos por vecindad; '
        'T7=1 y T4=2 elegidos por el usuario. No es una delimitación legal verificada. '
        'Votos por circunscripción de la tabla de Wikipedia, que cita al AGN y el expediente '
        '290-D-1955 de la HCDN; no se reparten ni ajustan votos. No hay padrón por circunscripción.')


def geometria(units):
    m = json.loads(MAPEO.read_text(encoding='utf-8'))['correspondencias']
    nums = {r['id_trazo']: r['circ_adoptada'] for r in m}
    assert set(nums) == set(nums.values()) == set(range(1, 15))
    data = json.loads((GEO/'shp/caba_1954_trazado_aproximado.geojson').read_text(encoding='utf-8'))
    capital = []
    for f in data['features']:
        t = f['properties']['id_trazo']; n = nums[t]; g = shape(f['geometry'])
        assert g.is_valid and not g.is_empty
        capital.append(dict(prov='Capital Federal', name=f'Circ. {n:02d}', circ=n,
                            id_trazo=t, kind='circunscripción', link=[], geom=g,
                            nota_geo=NOTE + f' Este polígono es T{t}; número adoptado: {n}.'))
    assert len(capital) == 14
    return [u for u in units if u['prov'] != 'Capital Federal'] + capital


def datos():
    text = FUENTE.read_text(encoding='utf-8')
    start = text.index('! colspan=6|[[Capital Federal]]')
    end = text.index('! colspan=6|[[Provincia', start)
    chunks = re.split(r'! rowspan=\d+\|(\d+)\.ª', text[start:end])
    blocs = {'Partido Peronista':'PP', 'Unión Cívica Radical':'UCR', 'Partido Comunista':'PC',
             'Partido Socialista de la Revolución Nacional':'PSRN',
             'Partido Demócrata Progresista':'PDP', 'Concentración Obrera':'CO'}
    out, controls = {}, []
    for i in range(1, len(chunks), 2):
        n, t = int(chunks[i]), chunks[i+1]
        rows = re.findall(r'\| align=left\|(\[\[.*?\]\])\s*\n\| ([\d.]+)\s*\n\| ([\d,]+)', t)
        parties = [(_clean(name), int(v.replace('.', '')), blocs[_clean(name)]) for name,v,_ in rows]
        totals = {label:int(v.replace('.', '')) for label,v in re.findall(
            r'\| colspan=2 align=left\|([^\n]+)\s*\n\|\s*([\d.]+)\s*\n', t)}
        assert len(parties) == 6, (n, parties)
        pos = sum(v for _,v,_ in parties)
        bla, nul, vot = (totals[k] for k in ('Votos en blanco','Votos anulados','Total de votos'))
        assert pos == totals['Votos positivos'] and pos+bla+nul == vot, (n, totals)
        out[('Capital Federal',str(n))] = dict(ins=None,vot=vot,bla=bla,nul=nul,
            parties=parties,bloc={b:v for _,v,b in parties},imput=False,est=False,
            cargo='diputados',solo_varones=False,
            nota='Votos de la tabla por circunscripción de Wikipedia (AGN/HCDN), sin padrón publicado.')
        controls.append(dict(circ=n,partidos=parties,positivos=pos,blancos=bla,anulados=nul,total=vot))
    assert {int(n) for _,n in out} == set(range(1,15))
    report = dict(fuente=str(FUENTE.relative_to(ROOT)),sha256=hashlib.sha256(FUENTE.read_bytes()).hexdigest(),
                  url='https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1954#Capital_Federal',
                  fuente_citada='AGN y expediente HCDN 290-D-1955',circunscripciones=controls,
                  total=sum(c['total'] for c in controls),sin_padron=True,
                  cartografia='Correspondencia provisional en numeracion_adoptada.json; votos publicados sin ajuste.')
    return out, report


def para_visor(original):
    """Conserva el CD de 20 secciones como variante, sin trasladar sus votos."""
    from copy import deepcopy
    rows, report = datos()
    cols = [('Partido Peronista','PP','#318ce7'),('Unión Cívica Radical','UCR','#e10019'),
            ('Partido Comunista','PC','#8b1a1a'),('Partido Socialista de la Revolución Nacional','PSRN','#ff7043'),
            ('Partido Demócrata Progresista','PDP','#005c9e'),('Concentración Obrera','CO','#795548')]
    U = {}
    for (_,n),r in rows.items():
        votes = {b:v for _,v,b in r['parties']}
        U[n] = dict(ins=None,vot=r['vot'],bla=r['bla'],nul=r['nul'],p=[votes[b] for _,b,_ in cols])
    e = deepcopy(original)
    e.update(g='g54',sexos=['T'],u={'T':U},nom={n:'' for n in U},
             cols=[dict(n=n,c=c,o=False) for n,_,c in cols],
             tot=dict(ins=None,vot=report['total'],p=[sum(r['p'][i] for r in U.values()) for i in range(len(cols))]),
             hayBla=True,hayNul=True,notas=[NOTE,
             'La planilla 62 del CD está por 20 secciones y suma 1.549.416 votantes; '
             'esta tabla de 14 circunscripciones suma 1.547.876. Se conservan ambos registros '
             'sin ajustar su diferencia de 1.540. El selector permite volver a las 20 secciones del CD, '
             'incluido su desglose por sexo.'],avisos=[],ilegibles=[],
             fuente='Wikipedia (AGN/HCDN), por circunscripción de 1954',
             original_cd=deepcopy(original))
    return e, report
