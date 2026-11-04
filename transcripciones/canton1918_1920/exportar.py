"""Exporta y controla la lectura visual; las discrepancias se conservan, nunca se imputan."""
from collections import Counter, defaultdict
from pathlib import Path
import csv, hashlib, json, re, sys, unicodedata

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf'

def norm(s):
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFD',str(s).lower()).encode('ascii','ignore').decode())

def export(year):
    folder=ROOT/f'transcripciones/canton{year}'
    source=folder/f'canton_{year}.json'
    doc=json.loads(source.read_text(encoding='utf-8-sig'))
    pages=doc['paginas'];expected=list(range(44,55)) if year==1918 else list(range(56,69))
    assert sorted(p['pagina_pdf'] for p in pages)==expected,(year,'páginas')
    cells=[];marks=Counter();rows_count=0;with_numbers=0;num_count=0;seen=set();alerts=[];partial=[];totals={};keys=[]
    md=[f'# Cantón: diputados nacionales {year}','','Transcripción visual del tomo II. Las cifras y marcas son las publicadas; las discrepancias aritméticas no se corrigen por residuo. Los encabezados y notas se conservan por página.','']
    for p in pages:
        cols={str(c):v for c,v in p['columnas'].items()}
        assert p['anio']==year
        keys.append(dict(provincia=p['provincia'],pagina_pdf=p['pagina_pdf'],pagina_impresa=p['pagina_libro'],columnas=cols,marcas_columnas=p.get('marcas_columnas',{}),notas=p.get('notas',p.get('nota','')),fuentes_impresas=p.get('fuentes_impresas',''),reserva_cronologica=p.get('reserva_cronologica','')))
        md += [f'## {p["provincia"]} · PDF {p["pagina_pdf"]} · libro {p["pagina_libro"]}','',p.get('eleccion','Diputados nacionales')+'; '+p.get('categoria','varones solamente')+'.','', '; '.join(f'{c}: {v}' for c,v in cols.items()),'']
        if p.get('marcas_columnas'):md += ['Marcas de encabezado: '+str(p['marcas_columnas']),'']
        for field in ('nota','notas','fuentes_impresas','reserva_cronologica'):
            if p.get(field):md += [str(p[field]),'']
        md += ['| Unidad | '+' | '.join(cols)+' |','|---|'+'---:|'*len(cols)]
        for r in p['filas']:
            rows_count+=1
            uid=(norm(p['provincia']),norm(r['unidad']))
            assert uid not in seen,(year,'fila duplicada',uid)
            seen.add(uid)
            values={str(c):v for c,v in r['valores'].items()};symbols={str(c):v for c,v in r.get('marcas',{}).items()}
            assert set(values).union(symbols)==set(cols),(year,p['pagina_pdf'],r['unidad'],'columnas distintas')
            numbers=[v for v in values.values() if v is not None]
            assert all(type(v) is int and v>=0 for v in numbers),(year,r['unidad'],'número inválido')
            with_numbers+=bool(numbers)
            for c,label in cols.items():
                value=values.get(c);symbol=symbols.get(c,'')
                assert value is not None or symbol,(year,p['pagina_pdf'],r['unidad'],c,'vacío sin marca')
                assert value is None or not symbol,(year,p['pagina_pdf'],r['unidad'],c,'valor y marca simultáneos')
                num_count+=value is not None
                if symbol:marks[symbol]+=1
                else:
                    bucket=totals.setdefault(p['provincia'],{});bucket[label]=bucket.get(label,0)+value
                origin=('encabezado' if str(p.get('marcas_columnas',{}).get(c))==symbol else 'celda') if symbol else ''
                note=' '.join(str(r.get(k,'')) for k in ('nota','nota_revision')).strip()
                cells.append(dict(anio=year,tomo='II',pagina_pdf=p['pagina_pdf'],pagina_libro=p['pagina_libro'],provincia=p['provincia'],eleccion=p['eleccion'],categoria=p['categoria'],unidad=r['unidad'],circunscripcion=r.get('circunscripcion'),columna=c,concepto=label,valor=value,marca=symbol,origen_marca=origin,nota=note,fuentes_impresas=p.get('fuentes_impresas',''),reserva_cronologica=p.get('reserva_cronologica','')))
            disp=r['unidad']+(f' ({r["circunscripcion"]})' if r.get('circunscripcion') else '')
            md.append('| '+disp+' | '+' | '.join(str(values.get(c)) if values.get(c) is not None else str(symbols[c]) for c in cols)+' |')
            ins=next((values.get(c) for c,label in cols.items() if norm(label)=='inscriptos'),None)
            vot=next((values.get(c) for c,label in cols.items() if norm(label)=='votantes'),None)
            vote_cols=[c for c,label in cols.items() if norm(label) not in ('inscriptos','votantes')]
            tab=sum(values.get(c) or 0 for c in vote_cols)
            unknown=[c for c in vote_cols if values.get(c) is None]
            if vot is not None and tab!=vot:
                alerts.append(dict(provincia=p['provincia'],unidad=r['unidad'],pagina_pdf=p['pagina_pdf'],votantes=vot,suma_columnas=tab,diferencia=tab-vot,columnas_sin_cifra=unknown,tipo='suma_mayor' if tab>vot else 'suma_menor'))
            if ins is not None and vot is not None and vot>ins:
                alerts.append(dict(provincia=p['provincia'],unidad=r['unidad'],pagina_pdf=p['pagina_pdf'],inscriptos=ins,votantes=vot,tipo='votantes_mayores_que_inscriptos'))
            if any(v is None for v in values.values()) and numbers:partial.append(dict(provincia=p['provincia'],unidad=r['unidad'],pagina_pdf=p['pagina_pdf'],marcas=symbols))
            if r.get('nota'):md += ['','Nota de '+r['unidad']+': '+r['nota'],'']
        md.append('')
    fields=list(cells[0])
    with (folder/f'canton_{year}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cells)
    (folder/f'TRANSCRIPCION_{year}.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    control=dict(anio=year,paginas=len(pages),distritos=len({p['provincia'] for p in pages}),filas=rows_count,filas_con_numeros=with_numbers,celdas=len(cells),numeros=num_count,marcas=dict(marks),vacios_sin_marca=0,sha256_pdf=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),sha256_transcripcion=hashlib.sha256(source.read_bytes()).hexdigest(),alertas_aritmeticas=alerts,filas_parciales=partial,sumas_columnas_por_distrito=totals,claves_por_pagina=keys,advertencia='Suma menor que votantes puede reflejar categorías omitidas; las marcas no equivalen a cero. No se corrigen discrepancias ni se infieren fuerzas por residuo.')
    (folder/f'CONTROL_{year}.json').write_text(json.dumps(control,ensure_ascii=False,indent=2),encoding='utf-8')
    differences=[f'# Diferencias y marcas del original: {year}','','Se preservan cifras impresas. Una alerta es una comprobación de coherencia, no una prueba de error ni de fraude. Las sumas incluyen solo las columnas publicadas con cifra; nunca se interpreta una marca como cero.','','| Provincia | PDF | Unidad | Votantes | Suma publicada | Diferencia | Columnas sin cifra |','|---|---:|---|---:|---:|---:|---|']
    for a in alerts:
        if 'diferencia' in a:differences.append(f'| {a["provincia"]} | {a["pagina_pdf"]} | {a["unidad"]} | {a["votantes"]} | {a["suma_columnas"]} | {a["diferencia"]} | {", ".join(a["columnas_sin_cifra"])} |')
    (folder/f'DIFERENCIAS_ORIGINAL_{year}.md').write_text('\n'.join(differences)+'\n',encoding='utf-8')
    print(year,{k:control[k] for k in ('paginas','distritos','filas','filas_con_numeros','celdas','numeros','marcas')})
    return control

if __name__=='__main__':
    for y in map(int,sys.argv[1:] or (1918,1920)):export(y)
