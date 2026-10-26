"""Consolidación explícita de transcripciones; no corrige ni imputa cifras."""
from pathlib import Path
import csv, json, shutil, hashlib
import pymupdf
from collections import defaultdict

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
FIELDS=['provincia','departamento','partido_o_lista','votos','fila_fuente','fuente_id','nota']

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def resolve(raw,part):
    if not raw:return None
    p=Path(raw)
    for candidate in [p,PROJECT/p,ROOT/p,part/p]:
        if candidate.is_file():return candidate.resolve()
    return None

def main():
    # Cantón permanece como referencia secundaria: no se mezcla con candidatos primarios.
    canton=read(ROOT/'partes/buenos_aires/datos.csv')+read(ROOT/'partes/canton_tres/datos.csv')
    write(ROOT/'datos_1914_canton_comparacion.csv',canton,FIELDS)
    # Fase2: derivación territorial explícita, NO concatenar con la principal.
    cordoba=read(ROOT/'fase2/cordoba/datos_principal_mas_complementaria.csv')
    corrientes=read(ROOT/'partes/corrientes/datos.csv')
    rioja=read(ROOT/'fase2/la_rioja/datos.csv')
    mendoza=read(ROOT/'fase2/mendoza/datos.csv')
    for r in mendoza:
        r['nota']='Elección principal del22/3/1914; excluye complementaria del5/4, conservada aparte. '+r['nota']
    # Las alternativas del resumen cordobés y las mesas anuladas de Jujuy NO entran.
    rows=[r for r in canton if r['provincia']!='Córdoba']+cordoba+corrientes+rioja+mendoza
    seen=set()
    for r in rows:
        assert set(FIELDS)<=set(r),r
        key=tuple(r[x] for x in ['provincia','departamento','partido_o_lista','fuente_id','fila_fuente'])
        assert key not in seen,('duplicado',key)
        seen.add(key)
        if r['votos']!='':assert r['votos'].isdigit(),r
        assert r['fila_fuente'] and r['fuente_id'] and r['nota'],r
    write(ROOT/'datos_1914_depto.csv',rows,FIELDS)
    # Evidencia de otros estados del cómputo, jamás sumable con la selección.
    partial=[]
    for path,level,state in [
        (ROOT/'fase3/santa_fe/datos_territoriales.csv','departamento','prensa anterior al cierre definitivo'),
        (ROOT/'partes/jujuy/datos.csv','mesa/circuito','deducción propuesta por Comisión'),
        (ROOT/'partes/jujuy/datos_nuevos.csv','subconjunto de mesa','votos ya anulados por Junta citados en debate')]:
        if path.exists():
            for r in read(path):
                partial.append(dict(r,nivel=r.get('nivel') or level,estado=r.get('estado') or state,archivo_original=str(path.relative_to(ROOT)).replace('\\','/')))
    path=ROOT/'fase2/tucuman/datos.csv'
    for r in read(path):
        partial.append(dict(provincia=r['provincia'],departamento=r['unidad'],partido_o_lista=r['candidato'],votos=r['votos'],fila_fuente=r['fila_fuente'],fuente_id=r['fuente_id'],nota=r['nota'],nivel=r['nivel'],estado=r['estado'],archivo_original=str(path.relative_to(ROOT)).replace('\\','/')))
    write(ROOT/'datos_1914_parciales.csv',partial,FIELDS+['nivel','estado','archivo_original','grupo_fuente','cobertura'])
    summary={}
    for r in rows:
        d=summary.setdefault(r['provincia'],{'filas':0,'cifras':0,'ausencias':0,'unidades':set(),'fuentes':set()})
        d['filas']+=1;d['cifras']+=r['votos']!='';d['ausencias']+=r['votos']==''
        d['unidades'].add(r['departamento']);d['fuentes'].add(r['fuente_id'])
    for d in summary.values():d['unidades']=len(d['unidades']);d['fuentes']=sorted(d['fuentes'])

    # Manifest único; conserva intentos fallidos y asignaciones reales en notas.
    sources=[]
    for p in [ROOT/'fuentes_hcdn.csv',ROOT/'fuentes_alternativas.csv',ROOT/'fase2/santa_fe/fuentes_continuacion.csv',ROOT/'fase2/entre_rios/fuentes_inferencia.csv']+sorted((ROOT/'partes').glob('*/fuentes.csv'))+sorted((ROOT/'partes').glob('*/fuentes_nuevas.csv'))+sorted((ROOT/'fase2').glob('*/fuentes.csv'))+sorted((ROOT/'fase3').glob('*/fuentes.csv')):
        if not p.exists():continue
        for n,r in enumerate(read(p),1):
            raw=r.get('archivo','')
            actual=resolve(raw,p.parent)
            if actual and actual.suffix.lower()=='.pdf' and not actual.is_relative_to(ROOT/'fuentes'):
                dest=ROOT/'fuentes'/actual.name
                if not dest.exists():shutil.copy2(actual,dest)
                actual=dest
            source_id=r.get('fuente_id') or (raw and Path(raw).stem) or f'{p.stem}_{n}'
            if not raw and r.get('url','').endswith('.pdf'):source_id=r['url'].split('/')[-1][:-4]
            entry=dict(fuente_id=source_id,provincia=r.get('provincia',''),url=r.get('url',''),fecha_consulta=r.get('fecha_consulta',r.get('fecha','2026-10-15')),tamano_bytes=actual.stat().st_size if actual else r.get('tamano_bytes','0'),estado=r.get('estado',''),archivo=str(actual.relative_to(ROOT)).replace('\\','/') if actual and actual.is_relative_to(ROOT) else raw,localizador=r.get('localizador',r.get('paginas','')),metodo=r.get('metodo','descarga pública; ver revisión de expedientes'),nota=' | '.join(x for x in [r.get('detalle',''),r.get('nota',''),'registro original: '+str(p.relative_to(ROOT)).replace('\\','/')] if x))
            ident=entry['url'].split('/')[-1].split('#')[0]
            real={'343-d-1914.pdf':('Entre Ríos','elección parcial noviembre 1914; no Tucumán general'), '12-d-1915.pdf':('Jujuy','elección abril 1915; no Tucumán general'), '5-d-1915.pdf':('Santiago del Estero','elección abril/mayo 1915; no Tucumán general'), '21-p-1914.pdf':('Buenos Aires','prueba de letra P; no Corrientes'), '29-d-1914.pdf':('Buenos Aires','prueba de letra D; no Mendoza')}.get(ident)
            if real:
                entry['provincia']=real[0];entry['nota']+=' | IDENTIDAD VERIFICADA: '+real[1]
                entry['estado']+='; excluido para el distrito/comicio inicialmente buscado'
            if raw and not actual:entry['nota']+=' | ruta original no resuelta: '+raw
            sources.append(entry)
    ids={r['fuente_id'] for r in sources}
    missing={r['fuente_id'] for r in rows+partial}-ids
    assert not missing,('fuentes sin registro',missing)
    write(ROOT/'fuentes.csv',sources,['fuente_id','provincia','url','fecha_consulta','tamano_bytes','estado','archivo','localizador','metodo','nota'])
    inventory=[]
    for p in sorted((ROOT/'fuentes').glob('*.pdf')):
        digest=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
        with pymupdf.open(p) as doc:
            pages=len(doc)
            for page in doc: page.get_text()
            inventory.append(dict(archivo=str(p.relative_to(ROOT)).replace('\\','/'),tamano_bytes=p.stat().st_size,paginas=pages,sha256=digest.hexdigest(),integridad='abierto y todas las páginas cargadas; no implica legibilidad visual ni verificación electoral'))
    write(ROOT/'inventario_pdfs.csv',inventory,['archivo','tamano_bytes','paginas','sha256','integridad'])
    result={'fecha':'2026-10-15','por_provincia':summary,'filas':len(rows),'cifras':sum(r['votos']!='' for r in rows),'ausencias':sum(r['votos']=='' for r in rows),'registros_fuentes':len(sources),'regla':'Córdoba: derivado principal más complementaria, excluye adiciones sin departamento; principal y variante conservadas aparte. La Rioja: mesas declaradas válidas por Comisión, no certificación de resolución de Cámara. Jujuy sigue investigado; sus deducciones parciales quedan aparte. Tucumán: debate y mesas impugnadas aparte. No sumar candidaturas como electores.'}
    result['parciales']={'filas':len(partial),'cifras':sum(r['votos']!='' for r in partial),'ausencias':sum(r['votos']=='' for r in partial),'santa_fe':sum(r['provincia']=='Santa Fe' for r in partial),'regla':'Santa Fe: siete resúmenes de prensa, tres totales impresos del 1/4 (Castellanos, Belgrano, Iriondo) y dos sumas territoriales incompletas (Capital, General López); niveles y grupos conservados. Jujuy/Tucumán: testimonios y estados distintos, no sumables con selección principal.'}
    (ROOT/'control_consolidacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
