"""Inventario reproducible de fuentes y agrupaciones; no modifica los originales."""
from pathlib import Path
import sys, json, re, urllib.request, urllib.parse, time, os
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'wikileg'))
from bloques_leg import match, wiki_groups
from bloques_prov import match_prov

def fetch(year):
    dst = ROOT/'wikileg'/f'wleg{year}.txt'
    if dst.exists(): return
    q = urllib.parse.urlencode(dict(action='parse',page=f'Elecciones legislativas de Argentina de {year}',prop='wikitext',format='json'))
    for attempt in range(5):
        try:
            req = urllib.request.Request('https://es.wikipedia.org/w/api.php?'+q, headers={'User-Agent':'AtlasElectoralArgentina/1.0 (%s)' % os.environ.get("ATLAS_CONTACT", "sin contacto; definir ATLAS_CONTACT")})
            data = json.load(urllib.request.urlopen(req,timeout=50))
            dst.write_text(data['parse']['wikitext']['*'],encoding='utf8')
            return
        except Exception:
            if attempt==4: raise
            time.sleep(3*(attempt+1))

if __name__=='__main__':
    fetch(2003)
    for year in range(2003,2026,2):
        path = ROOT/'datos_oficiales'/str(year)/('agregado_polar.pkl' if year<2011 else 'agregado.pkl')
        v,m=pd.read_pickle(path)
        v=v[v.cargo_nombre.str.contains('DIPUTAD')]
        print('\nYEAR',year,'filas',len(v),'positivos',int(v[v.votos_tipo=='POSITIVO'].v.sum()),'provincias',v.distrito_id.nunique(),flush=True)
        if year==2003:
            g=wiki_groups(year,'DIPUTADOS')
        elif year in (2005,2007,2009):
            g,mp,log,t=match_prov(year,'DIPUTADOS')
            print('SIN AGRUPAR',[(r.distrito_nombre,r.agrupacion_nombre,int(r.v)) for r in t.itertuples() if (r.distrito_nombre,r.agrupacion_nombre) not in mp and r.v>20000])
        else:
            g,d,mp,used=match(year,'DIPUTADOS')
            print('SIN AGRUPAR',[(n,int(v)) for n,v in d.items() if n not in mp and v>20000])
        print('GRUPOS',[(q['grupo'],q['total'],q['filas'][0]['color'] if q['filas'] else None) for q in g],flush=True)
        print('TDF',v[(v.distrito_id.astype(int)==24)&(v.votos_tipo=='POSITIVO')].groupby(['seccion_id','seccion_nombre']).v.sum().to_dict(),flush=True)
    d=pd.read_csv(ROOT/'raw/datar_2003_departamento_SIN_VALIDAR.csv')
    print('DATAR',d.columns.tolist(),d.head(2).to_dict('records'))
