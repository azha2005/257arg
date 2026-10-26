"""1914d→1916d: transcripciones, sin totales provinciales ni cifras estimadas."""
from pathlib import Path
import ast
import hashlib
import json
import re
import unicodedata
import pandas as pd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'fuentes_1914_1916'
IDS={'Capital Federal':'01','Buenos Aires':'02','Córdoba':'04','Corrientes':'05',
     'Entre Ríos':'08','La Rioja':'12','Mendoza':'13'}
PROV14={'CNS':'CON','CNT':'CON','PRV':'CON','CRB':'CON','DEM':'CON','PPO':'CON','CLA':'CON','LDI':'CON',
        'UCR':'UCR','SOC':'SOC','UC':'UC','IND':'IND'}
SUBSUMED={('02','JUAREZ'),('02','TRESARROYOS'),('02','GONZALESCHAVES'),('02','GONZALEZCHAVES'),
          ('04','GENERALROCA'),('04','PTEROQUESAENZPENA'),('13','GENERALALVEAR'),('13','MALARGUE')}

def norm(s):
    s=unicodedata.normalize('NFD',str(s).upper()).encode('ascii','ignore').decode()
    return re.sub('[^A-Z0-9]','',s)

def literal(file,name):
    for node in ast.parse((ROOT/file).read_text(encoding='utf8')).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(name)

def key(prov,name):
    d,n=IDS[prov],norm(name)
    aliases={'02':{'NUEVEDEJULIO':'9DEJULIO','LAMATANZA':'MATANZA','GONZALEZCHAVES':'GONZALESCHAVES'},
             '04':{'GENERALSANMARTIN':'TERCEROABAJO'},'05':{'PASODELOSLIBRES':'LIBRES','SANLUISDELPALMAR':'SANLUIS'},
             '08':{'URUGUAY':'CONCEPCIONDELURUGUAY','TALA':'ROSARIOTALA'},
             '12':{'JUAREZCELMAN':'GOBERNADORGORDILLO'},'13':{'CAPITAL':'CIUDAD','LUJANDECUYO':'LUJAN'}}
    n=aliases.get(d,{}).get(n,n)
    groups={'02':{'NECOCHEA','JUAREZ','BENITOJUAREZ','TRESARROYOS','GONZALESCHAVES'},
            '04':{'JUAREZCELMAN','GENERALROCA','PTEROQUESAENZPENA'},
            '05':{'SANMARTIN','GENERALALVEAR'},'13':{'SANRAFAEL','GENERALALVEAR','MALARGUE'}}
    if n in groups.get(d,set()):
        n={'02':'G:NECOCHEA','04':'G:JUAREZCELMAN','05':'G:SANMARTIN','13':'G:SANRAFAEL'}[d]
    else:n='S:'+n
    return d,0,n

def valid_candidates(pattern,value):
    pattern=str(pattern)
    options=[pattern]
    if pattern.endswith('?'):options.append(pattern[:-1])
    return any(re.fullmatch(p.replace('?','[0-9]'),str(int(value))) for p in options)

def geography_evidence(prov,name):
    d,_,c=key(prov,name)
    pages={'01':'PDF19: secciones censales; la correspondencia electoral usa los nombres de Cantón',
           '02':'Cuadro 1 PDF22–30; Anexo PDF65–68','04':'Cuadro 1 PDF32–33',
           '05':'Cuadro 1 PDF34–35','08':'Cuadro 1 PDF35–36','12':'Cuadro 1 PDF38–39','13':'Cuadro 1 PDF39–40'}
    return 'Cacopardo 1967, '+pages[d]+('; dato subsumido según Cantón, Apéndice C' if c.startswith('G:') else '')

def main():
    OUT.mkdir(exist_ok=True)
    sources=['transcripciones/busqueda1914/datos_1914_depto.csv','transcripciones/1916dip/canton_diputados_1916/celdas_1916.csv',
             'transcripciones/1916dip/canton_diputados_1916/cotejo_lupu_1916.csv','mapas/mapa1914/build_1914.py','mapas/mapa1916dip/build_1916.py','DTS 47_Cacopardo_1967.pdf']
    lab=literal('mapas/mapa1914/build_1914.py','LAB')
    accompany=literal('mapas/mapa1914/build_1914.py','ACOMP')
    code16=literal('mapas/mapa1916dip/build_1916.py','CODE')
    demo=literal('mapas/mapa1916dip/build_1916.py','DEMOCRATA')
    bloc16=literal('mapas/mapa1916dip/build_1916.py','BLOC')
    ledger=[];records=[];excluded=[];kept={};discarded_cells=[]
    def save(year,observations,invalid):
        v=[]
        for (p,name),values in observations.items():
            k=key(p,name)
            if k in invalid:continue
            for code,value in values.items():
                v.append(dict(distrito_id=k[0],seccion_id=0,circuito=k[2],agrupacion_id=code,votos_tipo='POSITIVO',v=int(value)))
        v=pd.DataFrame(v).groupby(['distrito_id','seccion_id','circuito','agrupacion_id','votos_tipo'],as_index=False).v.sum()
        e=v.groupby(['distrito_id','seccion_id','circuito']).v.sum()
        assert e.min()>0
        pd.to_pickle((v,e),HERE/f'circ_{year}.pkl')
        kept[year]=dict(unidades=len(e),votos=int(e.sum()),por_provincia=e.groupby(level=0).agg(['size','sum']).to_dict('index'))
    src=pd.read_csv(ROOT/sources[0],keep_default_na=False)
    observations={};invalid=set()
    for (p,name),g in src.groupby(['provincia','departamento']):
        k=key(p,name);values={};errors=[]
        required=set(lab[p])
        found=set()
        all_missing=all(str(v)=='' for v in g.votos)
        subsumed=all_missing and ((k[0],norm(name)) in SUBSUMED)
        for row in g.itertuples():
            label=row.partido_o_lista
            if label in ('En blanco','Votos en blanco') or label in accompany.get(p,set()):continue
            code=lab[p].get(label,'OTR')
            found.add(label)
            if row.votos=='':
                if label in required:errors.append('Cifra faltante: '+label)
                continue
            if 'total es parcial' in row.nota.lower() or 'principal sin cifra' in row.nota.lower():errors.append('Cómputo parcial en '+label)
            value=int(float(row.votos))
            values[PROV14.get(code,'OTR')]=values.get(PROV14.get(code,'OTR'),0)+value
            ledger.append(dict(anio='1914d',provincia=p,departamento=name,partido=label,bloque=PROV14.get(code,'OTR'),votos=value,estado='cifra_publicada',fuente=row.fuente_id,localizador=row.fila_fuente,nota=row.nota))
        errors+=['Columna no publicada: '+label for label in required-found]
        if not values:errors.append('Sin votos desglosados')
        if errors:
            if not subsumed:invalid.add(k)
            excluded.append(dict(anio='1914d',provincia=p,departamento=name,clave=k[2],motivo='Subsumido en unidad mayor' if subsumed else '; '.join(errors)))
        else:observations[(p,name)]=values
        records.append(dict(anio='1914d',distrito=k[0],seccion=0,circuito=name,seccion_comun=0,circuito_comun=k[2],motivo='Dato único para territorio común; no se clonan polígonos',fuente_id=geography_evidence(p,name)))
    save('1914d',observations,invalid)
    cells=pd.read_csv(ROOT/sources[1])
    cells=cells[(cells.tipo=='votos') & cells.distrito.isin(IDS)]
    cross=pd.read_csv(ROOT/sources[2])
    for year,recovered in [('1916d',False),('1916de',True)]:
        observations={};invalid=set()
        for (p,name),g in cells.groupby(['distrito','unidad']):
            k=key(p,name);values={};errors=[]
            subsumed=(g.estado=='subsumido_o_no_considerado').all()
            for row in g.itertuples():
                code=demo[p] if row.variable=='Demócrata' else code16[row.variable]
                value=row.valor;state=row.estado
                if state not in ('numero_legible','transcripcion_visual_previa'):
                    matches=cross[(cross.distrito==p)&(cross.unidad==name)&(cross.columnas_canton==row.variable)&cross.valor_lupu.notna()]
                    if recovered and state=='lectura_no_resuelta' and len(matches)==1 and valid_candidates(row.lectura,matches.iloc[0].valor_lupu):
                        value=matches.iloc[0].valor_lupu;state='recuperado_Lupu_Stokes'
                    else:
                        errors.append(row.variable+': '+state)
                        if year=='1916d':discarded_cells.append(dict(provincia=p,departamento=name,variable=row.variable,lectura=row.lectura,estado=state))
                        continue
                values[bloc16[code]]=values.get(bloc16[code],0)+int(value)
                if year=='1916d' or state=='recuperado_Lupu_Stokes':
                    ledger.append(dict(anio=year,provincia=p,departamento=name,partido=row.variable,bloque=bloc16[code],votos=int(value),estado=state,fuente='cotejo_lupu_1916.csv' if state=='recuperado_Lupu_Stokes' else 'celdas_1916.csv',localizador=f'PDF {row.pagina_pdf_original}, página {row.pagina_impresa}, columna {row.columna}',nota='Fuente observada; no se usan estimaciones del atlas'))
            if not values:errors.append('Sin votos desglosados')
            if errors:
                if not subsumed:invalid.add(k)
                excluded.append(dict(anio=year,provincia=p,departamento=name,clave=k[2],motivo='Subsumido en unidad mayor' if subsumed else '; '.join(errors)))
            else:observations[(p,name)]=values
            records.append(dict(anio=year,distrito=k[0],seccion=0,circuito=name,seccion_comun=0,circuito_comun=k[2],motivo='Dato único para territorio común; no se clonan polígonos',fuente_id=geography_evidence(p,name)))
        save(year,observations,invalid)
    pd.DataFrame(ledger).to_csv(OUT/'cifras_y_fuentes.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(records).to_csv(OUT/'correspondencias.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(excluded).to_csv(OUT/'exclusiones_fuente.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(discarded_cells).to_csv(OUT/'lecturas_no_usadas_en_principal.csv',index=False,encoding='utf-8-sig')
    manifest=dict(datos=kept,fuentes=[dict(ruta=s,sha256=hashlib.sha256((ROOT/s).read_bytes()).hexdigest()) for s in sources],
                  reserva='Cobertura parcial de siete jurisdicciones. Votos atribuidos a fuerzas/primer candidato publicado; no son necesariamente sufragantes únicos. Sin abstención, blancos ni totales provinciales repetidos.')
    (OUT/'control_preparacion.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(kept,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
