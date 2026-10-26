"""Controles de integridad del atlas y del paquete final, independientes del build."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,sys
from lxml import etree
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'../commons'))
from config import ATLAS
YEARS=list(range(2003,2026,2))
NEW={2003,2005,2007,2011,2015,2017,2019,2021,2023,2025}
report=[];errors=[]
for y in YEARS:
    ds=json.loads((ROOT/f'../mapas/mapa{y}/dataset_{y}.json').read_text(encoding='utf8'))
    cfg=ATLAS[str(y)];sub=ROOT/f'../commons/{y}/subir'
    modes=ds['modes'];gan=next(m for m in modes if m['id']=='gan')
    observed={r['w'] for r in gan['units'] if r.get('w')}
    legend={c['code'] for c in gan['national']['cands']}
    if y in NEW:
        tolhuin=[t for t in ds['territories'] if t['p']=='Tierra del Fuego' and t['n']=='Tolhuin']
        assert bool(tolhuin)==(y>=2019),(y,'Tolhuin anacrónico o ausente')
        if observed!=legend:errors.append([y,'leyenda y ganadores no coinciden',list(observed^legend)])
        W=json.loads((ROOT/f'../mapas/mapa{y}/wiki_nacional_{y}.json').read_text(encoding='utf8'))
        if sum(W['blocs'].values())+W['otros']!=W['positivos']:errors.append([y,'nacional no cierra'])
        for m in modes:
            for i,r in enumerate(m['units']):
                for lab,value in r.get('metrics',[]):
                    if lab=='Participación' and float(value.replace('%','').replace(',','.').strip())>100:errors.append([y,m['id'],i,'participación >100'])
    c=Counter(p.suffix for p in sub.glob('*') if p.is_file())
    if c['.svg']<2*len(modes):errors.append([y,'faltan SVG',dict(c)])
    if c['.png']<len(modes):errors.append([y,'faltan PNG',dict(c)])
    expected_s=len(modes)*(2+bool(cfg.get('sin_logo')))
    if c['.svg']!=expected_s:errors.append([y,'cantidad de SVG inesperada',c['.svg'],expected_s])
    pngs=list(sub.glob('*.png'))
    for m in modes:
        prefix=f'Elecciones legislativas de Argentina de {y} - '
        # La copia de PNG normal debe coincidir bit a bit con el render final.
        normal=[p for p in pngs if '(siglas)' not in p.name]
        source=ROOT/f'../png_transparentes/mapa{y}/atlas_{y}_{m["id"]}.png'
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if not any(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p in normal):errors.append([y,m['id'],'PNG del paquete difiere del render final'])
    for p in sub.glob('*.svg'):
        etree.parse(str(p))
        t=p.read_text(encoding='utf8')
        if re.search(r'<script|foreignObject|javascript:|<style|\bvar\(',t):errors.append([y,p.name,'construcción SVG no admitida'])
        if not p.with_name(p.name+'.txt').exists():errors.append([y,p.name,'sin wikitext'])
    legend_files=[p for p in sub.glob('*Resultados por departamento (con leyenda).svg')]
    if legend_files:
        t=legend_files[0].read_text(encoding='utf8').lower()
        for code in legend:
            color=ds['candidates'][code]['base'].lower()
            if color not in t:errors.append([y,code,color,'color ausente en SVG con leyenda'])
    report.append(dict(year=y,modes=len(modes),svg=c['.svg'],png=c['.png'],wikitext=c['.txt'],hold=cfg['hold'],hold_logos=cfg['hold_logos']))
ds=json.loads((ROOT/'../mapas/mapa2025/dataset_2025.json').read_text(encoding='utf8'))
assert next(x for x in ds['candidates'].values() if x['n']=='Provincias Unidas')['base'].lower()=='#ff682c'
result=dict(atlases=report,errors=errors)
(ROOT/'../commons/CONTROL_ENTREGA_LEGISLATIVAS_2003_2025.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if errors:sys.exit(1)
