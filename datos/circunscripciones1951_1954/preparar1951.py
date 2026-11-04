"""Transcribe las tablas HTML preservadas; no infiere votos ni cierres."""
from pathlib import Path
from lxml import html
from collections import Counter
import json, re
HERE=Path(__file__).resolve().parent
t=html.fromstring((HERE/'wiki1951.html').read_text(encoding='utf8'))
def clean(s):return re.sub(r'\[[^\]]*\]', '',s).replace('\xa0',' ').strip()
def number(s):
    s=clean(s).replace('.','').replace(' ','').replace('–','-').replace('−','-')
    return int(s) if re.fullmatch(r'-?\d+',s) else None
def code(s):
    if s.startswith('Partido Peronista'):return 'PP'
    if s.startswith('Unión Cívica Radical'):return 'UCR'
    if s.startswith('Partidos varios'):return 'OTR'
    return {'Partido Demócrata':'PD','Partido Socialista':'PS','Partido Comunista':'PC','Concentración Obrera':'CO','Partido Demócrata Progresista':'PDP','Unión Cívica Nacionalista':'UCN','Partidos varios':'OTR'}.get(s)
tables=[x for x in t.xpath('//table') if len(x.xpath('./tbody/tr|./tr'))>80 and 'N.º' in x.text_content()[:200]]
assert len(tables)==2
records=[]; province=None; current=None; special=False
for table in tables:
    for row in table.xpath('./tbody/tr|./tr'):
        cells=[clean(c.text_content()) for c in row.xpath('./th|./td')]
        if not cells:continue
        text=cells[0]
        if re.match(r'^(Provincia|Capital Federal|Territorio nacional|Gobernación Militar)',text):
            province=re.sub(r'\d+\s*(Diputados?|Delegados?).*$', '',text).strip()
            province=re.sub(r'^(Provincia de |Territorio nacional de |Territorio nacional del |Gobernación Militar de )','',province)
            province={'la Tierra del Fuego':'Tierra del Fuego','la Rioja':'La Rioja','del Río Negro':'Río Negro','Neuquén':'Neuquén'}.get(province,province)
            special=not text.startswith(('Provincia','Capital')) and re.search(r'1 Delegado',text) is not None
            current=None
            continue
        if not province or text.startswith(('N.º','Fuente:')):continue
        if re.match(r'^\d+\.ª$',text):
            current=dict(provincia=province,numero=int(text.split('.')[0]),cargo='delegado' if table is tables[1] else 'diputado',candidatos=[],metricas={})
            records.append(current); cells=cells[1:]
        # Columnas de color vacías preceden al nombre de partido.
        party_index=next((i for i,c in enumerate(cells) if code(c)),None)
        if party_index is not None:
            if current is None and special:
                current=dict(provincia=province,numero=1,cargo='delegado',candidatos=[],metricas={});records.append(current)
            if current is None: raise ValueError(cells)
            i=party_index
            value=number(cells[i+1])
            if cells[i+1]=='—' and cells[i+2]=='0.00 %': value=0
            assert value is not None, cells
            current['candidatos'].append(dict(partido=cells[i],codigo=code(cells[i]),votos=value,literal_votos=cells[i+1],nombre=cells[i+3] if len(cells)>i+3 else '',porcentaje_fuente=cells[i+2]))
        elif current and text in ('Votos positivos','Votos en blanco y anulados','Diferencia de votos','Total de votos','Registrados/participación'):
            current['metricas'][text]=number(cells[1])
        elif any(c.startswith('Partido') or c.startswith('Unión Cívica') for c in cells):
            raise ValueError(cells)
assert len(records)==150,(len(records),Counter(r['provincia'] for r in records))
differences=[]
for r in records:
    total=sum(c['votos'] for c in r['candidatos'])
    if total!=r['metricas'].get('Votos positivos'):
        differences.append(dict(provincia=r['provincia'],numero=r['numero'],suma=total,positivos=r['metricas'].get('Votos positivos')))
(HERE/'resultados1951.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
(HERE/'control_tablas1951.json').write_text(json.dumps(dict(unidades=len(records),por_distrito=dict(Counter(r['provincia'] for r in records)),diferencias= differences,totales=dict(sum((Counter({c['codigo']:sum(x['votos'] for x in r['candidatos'] if x['codigo']==c['codigo']) for c in r['candidatos']}) for r in records),Counter()))),ensure_ascii=False,indent=2),encoding='utf8')
print('UNIDADES',len(records),Counter(r['provincia'] for r in records),'CIERRES',differences)
