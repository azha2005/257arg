"""Proyección condicional de Diputados para los escenarios del usuario."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import itertools
import json
import re
import csv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf8'))

def magnitudes(year):
    folder = 'mapa1983dip' if year == 1983 else 'mapa1985'
    text = (ROOT/f'mapas/{folder}/w{year}.txt').read_text(encoding='utf8')
    table = text.split('== Cargos a elegir ==')[1].split('|}')[0]
    out = {}
    for block in table.split('|-'):
        match = re.search(r'!\s*\[\[([^\]]+)\]\]',block)
        if not match:
            continue
        name = match[1].split('|')[-1]
        nums = [int(n) for n in re.findall(r'^\|\s*(\d+)\s*$',block,re.M)]
        out[name] = nums[-1]
    assert sum(out.values()) == (254 if year == 1983 else 127)
    return out

def official_rolls(year):
    folder = 'mapa1983dip' if year == 1983 else 'mapa1985'
    text = (ROOT/f'mapas/{folder}/w{year}.txt').read_text(encoding='utf8')
    out = {}
    headers = list(re.finditer(r'!\s*colspan\s*=\s*\d+\s*\|\s*\[\[([^\]]+)\]\][^\n]*?<br\s*/?>\s*\d+\s*Diputados',text,re.I))
    for i,head in enumerate(headers):
        table = text[head.end():headers[i+1].start() if i+1<len(headers) else len(text)]
        name = head[1].split('|')[-1]
        name = re.sub(r'^(Provincia del? |Territorio Nacional de )','',name).replace(' (Argentina)','')
        if 'Tierra del Fuego' in name: name = 'Tierra del Fuego'
        match = re.search(r'Votantes registrados/participación\s*\n\|[^\n]*?([\d.]+)\s*\n',table)
        if match:
            out[name] = int(match[1].replace('.',''))
    return out

def votes(record, year):
    v = Counter()
    for code,n,_ in record['lines']:
        if code in ('P_BLA','P_NUL'):
            continue
        code = code.removeprefix('P_')
        # Solo se unen listas radicales aliadas y el bloque peronista ya unido.
        if code in ('ucr','ucrmpc'): code = 'UCR'
        elif code in ('pj','frejuli'): code = 'PJ'
        else: code = code.upper()
        v[code] += n
    return v

def dhondt(v, seats, roll):
    eligible = {c:n for c,n in v.items() if 100*n >= 3*roll and n>0}
    order = sorted(((Fraction(n,k),n,c) for c,n in eligible.items() for k in range(1,seats+1)),reverse=True)
    return Counter(c for _,_,c in order[:seats])

def balanced_cohorts(seats, retain):
    # Un reparto parejo por fuerza y distrito: piso/techo de la mitad.
    base = {c:n//2 for c,n in seats.items()}
    odd = [c for c,n in seats.items() if n%2]
    extra = retain-sum(base.values())
    options = []
    for chosen in itertools.combinations(odd,extra):
        opt = Counter(base)
        opt.update(chosen)
        options.append(opt)
    assert options
    return options

def run():
    ds = {1983:load('mapas/mapa1983hipotetico/dataset_1983_hipotetico.json'),
          1985:load('mapas/mapa1985peronismo/dataset_1985_peronismo.json')}
    mags = {y:magnitudes(y) for y in ds}
    rolls = {y:official_rolls(y) for y in ds}
    result = {y:Counter() for y in ds}
    district = {}
    audit = []
    for p in mags[1983]:
        district[p] = {}
        for y in ds:
            r = ds[y]['modes'][0]['prov'][p]
            roll = rolls[y].get(p)
            if roll is None:
                roll = int(dict(r['metrics'])['Inscriptos'].replace('.',''))
                audit.append(f'{y} {p}: padrón de la base del atlas')
            v = votes(r,y)
            s = dhondt(v,mags[y][p],roll)
            assert sum(s.values()) == mags[y][p]
            result[y].update(s)
            district[p][str(y)] = dict(seats=dict(s),votes=dict(v),roll=roll,magnitude=mags[y][p])
    # Retención ilustrativa: mitad equilibrada por fuerza y provincia;
    # sobrantes según el voto de 1983. No reproduce un sorteo contrafáctico.
    retained = Counter()
    lows = Counter()
    highs = Counter()
    for p, years in district.items():
        s = years['1983']['seats']
        n = mags[1983][p]-mags[1985][p]
        opts = balanced_cohorts(s,n)
        v = years['1983']['votes']
        central = max(opts,key=lambda o:sum(v.get(c,0) for c in o if o[c]>s[c]//2))
        retained.update(central)
        for c in s:
            lows[c] += min(o.get(c,0) for o in opts)
            highs[c] += max(o.get(c,0) for o in opts)
        years['retained_illustrative'] = dict(central)
    full85 = result[1985]+retained
    assert sum(retained.values()) == 127
    assert sum(full85.values()) == 254
    parties = sorted(set(result[1983])|set(full85))
    rows = [dict(party=c,total1983=result[1983][c],elected1985=result[1985][c],
                 retained_illustrative=retained[c],total1985_illustrative=full85[c],
                 balanced_min1985=result[1985][c]+lows[c],balanced_max1985=result[1985][c]+highs[c]) for c in parties]
    output = dict(assumption1983='Voto legislativo idéntico al presidencial hipotético por provincia; no es una proyección del corte de boleta histórico.',
                  assumption1985='Listas de FREJULI y renovadores unidas; escenario territorial ya generado.',
                  retained='Reparto equilibrado por partido y distrito, piso o techo de la mitad; central con extras según votos de 1983. Rangos individuales no necesariamente simultáneos.',
                  official_rolls_found={y:len(r) for y,r in rolls.items()},notes=audit,
                  summary=rows,districts=district)
    (HERE/'resultado.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    with (HERE/'bancas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(dict(rolls=output['official_rolls_found'],notes=audit,summary=rows),ensure_ascii=False,indent=2))

if __name__ == '__main__':
    run()
