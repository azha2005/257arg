from pathlib import Path
import json, csv, collections, unicodedata, zipfile, shutil

ROOT=Path(__file__).parent
OUT=ROOT/'resultado'
OUT.mkdir(exist_ok=True)
cells=[]; units=[]; legends=[]
def value(raw):
    if raw.isdigit(): return int(raw),'numero_legible'
    return None, {'**':'subsumido_o_no_considerado','*':'sin_datos','-':'guion_sin_cifra'}.get(raw,'lectura_no_resuelta')
for line in (ROOT/'transcripcion.txt').read_text().splitlines():
    if line.startswith('@'):
        province,page,*parties=line[1:].split('|');page=int(page)
        labels=['Inscriptos','Votantes']+parties
        for c,label in enumerate(labels,1):
            legends.append(dict(distrito=province,pagina_extracto=page,columna=c,rotulo=label))
        continue
    name,*raws=line.split('|')
    assert len(raws)==len(labels),(province,name,raws,labels)
    unit=dict(anio=1916,cargo='Diputados nacionales',distrito=province,unidad=name,pagina_extracto=page,pagina_pdf_original=page+27,pagina_impresa=page+16)
    units.append(unit)
    for c,(label,raw) in enumerate(zip(labels,raws),1):
        v,state=value(raw)
        cells.append(dict(**unit,columna=c,variable=label,tipo='votos' if c>=3 else 'padron',lectura=raw,valor=v,estado=state))

# Capital: reutilizar los 80 valores visualmente transcritos en el paquete anterior.
capital=json.loads((ROOT/'capital_federal_1916_canton_fuerzas_separadas.json').read_text())
capital_labels=['Unión Cívica Radical','Socialista','Socialista Argentino','Demócrata Progresista']
seen=set()
for r in capital:
    unit=dict(anio=1916,cargo='Diputados nacionales',distrito='Capital Federal',unidad=r['unidad'],pagina_extracto=1,pagina_pdf_original=28,pagina_impresa=17)
    if r['unidad'] not in seen: units.append(unit);seen.add(r['unidad'])
    cells.append(dict(**unit,columna=capital_labels.index(r['fuerza_literal'])+3,variable=r['fuerza_literal'],tipo='votos',lectura=str(r['votos']),valor=r['votos'],estado='transcripcion_visual_previa'))
unit=dict(anio=1916,cargo='Diputados nacionales',distrito='Capital Federal',unidad='Puerto',pagina_extracto=1,pagina_pdf_original=28,pagina_impresa=17)
units.append(unit)
for i,label in enumerate(capital_labels,3):
    cells.append(dict(**unit,columna=i,variable=label,tipo='votos',lectura='-',valor=None,estado='guion_sin_cifra'))
for i,label in enumerate(capital_labels,3): legends.append(dict(distrito='Capital Federal',pagina_extracto=1,columna=i,rotulo=label))

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c) and c.isalnum())
aliases={
 'camapana':'campana','chascomis':'chascomus','clavarria':'olavarria',
 'trenquelanguen':'trenquelauquen','mburcuya':'mburucuya',
 'governadorgordillo':'gobernadorgordillo','governadorvicentedupuy':'gobernadorvicentedupuy',
 'zonanacpuertolaplata':'zonaesppuertolaplata','nuevedejulio':'9dejulio',
 'nuevodejulio':'9dejulio','nuevedejuli':'9dejulio',
 'valleviego':'valleviejo','eumahuaca':'humahuaca'
}
def key(p,n):
    n=norm(n);return norm(p),aliases.get(n,n)
prior=json.loads((ROOT/'lupu_stokes_1916_diputados_agrupados.json').read_text())
index={key(r['province'],r['department']):r for r in prior}
groups=collections.defaultdict(dict)
for c in cells:
    if c['tipo']=='votos':groups[(c['distrito'],c['unidad'])][c['variable']]=c
comparison=[]
unmatched=[]
for (p,n),g in groups.items():
    r=index.get(key(p,n))
    if r is None:
        unmatched.append(dict(distrito=p,unidad=n,estado='sin_fila_equivalente_en_exportacion_lupu'))
        continue
    recipes={'ucr':['Unión Cívica Radical']}
    if p=='Capital Federal':recipes.update(soc=['Socialista'],con=['Socialista Argentino','Demócrata Progresista'])
    elif p=='Corrientes':recipes['con']=['Liberal','Autonomista']
    elif p=='Santa Fe':recipes={'ucr':['Radical disidente','Radical situacionista (Comité Nacional)'],'con':['Demócrata']}
    elif p=='San Luis':recipes['con']=['Demócrata']
    elif p=='La Rioja':recipes['con']=['Provincialista']
    elif p=='Jujuy':recipes['con']=['Provincialista']
    elif p=='Córdoba':recipes['con']=['Demócrata']
    elif p in ['Catamarca','Entre Ríos']:recipes['con']=['Concentración']
    else:recipes.update(con=['Conservador'],soc=['Socialista'])
    for family,labels in recipes.items():
        cc=[g[x] for x in labels]
        v=sum(c['valor'] for c in cc) if all(c['valor'] is not None for c in cc) else None
        other=r[family]
        state='coincide' if v is not None and other is not None and v==other else 'diferencia' if v is not None and other is not None else 'no_comparable_por_faltantes'
        comparison.append(dict(distrito=p,unidad=n,familia_lupu=family,columnas_canton=' + '.join(labels),valor_canton=v,valor_lupu=other,diferencia=v-other if v is not None and other is not None else None,estado=state,recid_lupu=r['recid']))

votes=[c for c in cells if c['tipo']=='votos']
coverage=[]
for p in sorted(set(u['distrito'] for u in units)):
    u=[r for r in units if r['distrito']==p];v=[c for c in votes if c['distrito']==p]
    coverage.append(dict(distrito=p,filas_territoriales=len(u),filas_con_algun_voto=sum(any(c['valor'] is not None for c in v if c['unidad']==r['unidad']) for r in u),celdas_votos=len(v),votos_numericos=sum(c['valor'] is not None for c in v),lecturas_votos_pendientes=sum(c['estado']=='lectura_no_resuelta' for c in v),marcas_sin_cifra=sum(c['valor'] is None and c['estado']!='lectura_no_resuelta' for c in v)))
diagnostic=dict(filas_territoriales=len(units),celdas=len(cells),celdas_votos=len(votes),votos_numericos=sum(c['valor'] is not None for c in votes),estados_celdas=dict(collections.Counter(c['estado'] for c in cells)),cotejo=dict(collections.Counter(c['estado'] for c in comparison)),distritos=len(coverage))
outputs={'celdas_1916':cells,'votos_1916':votes,'padron_1916':[c for c in cells if c['tipo']=='padron'],'claves_1916':legends,'cobertura_1916':coverage,'cotejo_lupu_1916':comparison,'unidades_sin_equivalencia_lupu':unmatched,'lecturas_pendientes':[c for c in cells if c['estado']=='lectura_no_resuelta']}
for name,rows in outputs.items():
    (OUT/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    if rows:
        with (OUT/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(OUT/'diagnostico.json').write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2))
for name in ['transcripcion.txt','construir.py','canton_1916_diputados_tablas.pdf','capital_federal_1916_canton_fuerzas_separadas.json','lupu_stokes_1916_diputados_agrupados.json']:
    shutil.copy2(ROOT/name,OUT/name)
assert len({(u['distrito'],u['unidad']) for u in units})==len(units),'unidades duplicadas'
assert len({(c['distrito'],c['unidad'],c['columna']) for c in cells})==len(cells),'celdas duplicadas'
print(json.dumps(diagnostic,ensure_ascii=False,indent=2))
print(json.dumps(coverage,ensure_ascii=False,indent=2))
print('DIFERENCIAS',json.dumps([c for c in comparison if c['estado']=='diferencia'],ensure_ascii=False))
