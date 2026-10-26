from pathlib import Path
import pandas as pd,csv,json,re,shutil,zipfile
root=Path(__file__).resolve().parent;raw=root/'../raw';prepared=root/'../datos/preparados';prepared.mkdir(exist_ok=True)
for a,b in [('/tmp/argentina_ecological_data.dta','lupu_stokes_1912_2003.dta'),('/tmp/2003-departamento.csv','datar_2003_departamento_SIN_VALIDAR.csv'),('/tmp/polar_pres2003.csv','polar_presidente_2003_mesas_SIN_VALIDAR.csv'),('/tmp/polar_listas2003.csv','polar_listas_presidente_2003.csv'),('/tmp/fix2003.R','polar_correccion_2003.R')]:
 if not (raw/b).exists():shutil.copyfile(a,raw/b)
d=pd.read_stata(raw/'lupu_stokes_1912_2003.dta');d.to_csv(prepared/'lupu_stokes_1912_2003_exportacion.csv',index=False)
coverage=[]
for (year,month,dip,pres),g in d.groupby(['year','month','dip','pres'],dropna=False):
 cat='Diputados nacionales' if dip else 'Presidente'
 if year==1954 and pres:cat='Vicepresidente (excluir de presidenciales)'
 if year==1957 or (year==1948 and month==12):cat='Constituyentes (excluir de diputados)'
 coverage.append({'anio':int(year),'mes':int(month) if pd.notna(month) else '', 'categoria':cat,'filas_departamento':len(g),'provincias_en_archivo':g.province.nunique(),**{f'filas_con_{c}':int(g[c].notna().sum()) for c in ['total','ucr','pj','soc','con']}})
pd.DataFrame(coverage).to_csv(prepared/'cobertura_lupu_stokes.csv',index=False)
# Entre Rios: unir tablas con ambos sexos sin las tablas provinciales ni las parciales por sexo.
manifest=json.loads((raw/'entre_rios_2001'/'procedencia.json').read_text());combined=[]
for item in manifest:
 fn=item['archivo'];depto=fn.removeprefix('eleccion-diputado-nac-').removesuffix('-20011014.csv').upper()
 for row in csv.DictReader((raw/'entre_rios_2001'/fn).open(encoding='utf-8-sig')):
  row={k.replace('-','_'):v for k,v in row.items()}
  combined.append({'anio':2001,'categoria':'Diputados nacionales','provincia':'Entre Ríos','departamento_archivo':depto,'fuerza_original':row['partidos_politicos_nombre'],'votos':row['partidos_politicos_votos'],'porcentaje_original':row['partidos_politicos_votos_porcentaje'],'fuente_url':item['url']})
pd.DataFrame(combined).to_csv(prepared/'entre_rios_diputados_2001_por_departamento.csv',index=False)
# Diagnosticos sin alterar los archivos originales.
x=pd.read_csv(raw/'datar_2003_departamento_SIN_VALIDAR.csv',dtype=str).fillna('');issues=[]
for i,r in x.iterrows():
 v=r.votos
 if v and not v.isdigit():issues.append({'archivo':'datar','fila_datos':i+1,'provincia':r.provincia,'departamento':r.departamento,'categoria':r.eleccion,'fuerza':r.partido,'problema':'valor no entero literal / separador de miles pendiente','valor_original':v})
 elif not v:issues.append({'archivo':'datar','fila_datos':i+1,'provincia':r.provincia,'departamento':r.departamento,'categoria':r.eleccion,'fuerza':r.partido,'problema':'votos ausentes','valor_original':v})
pd.DataFrame(issues).to_csv(prepared/'datar_2003_valores_para_revisar.csv',index=False)
p=pd.read_csv(raw/'polar_presidente_2003_mesas_SIN_VALIDAR.csv',dtype={'codprov':str,'coddepto':str,'circuito':str,'mesa':str})
votecols=list(p.columns[6:]);p['votos_suma']=p[votecols].sum(axis=1);flag=p.votos_suma>p.electores
p.loc[flag].to_csv(prepared/'polar_2003_mesas_para_revisar.csv',index=False)
a=p.groupby(['codprov','coddepto','depto'],as_index=False)[votecols+['electores']].sum();f=p.groupby(['codprov','coddepto','depto'],as_index=False).size().rename(columns={'size':'mesas_en_fuente'});a=a.merge(f);f2=p.loc[flag].groupby(['codprov','coddepto','depto'],as_index=False).size().rename(columns={'size':'mesas_votos_superan_electores'});a=a.merge(f2,how='left').fillna({'mesas_votos_superan_electores':0});a['estado_validacion']='PENDIENTE: no equivale a escrutinio definitivo';a.to_csv(prepared/'polar_presidente_2003_agregado_depto_SIN_VALIDAR.csv',index=False)
summary={'lupu_filas':len(d),'lupu_combinaciones_categoria':len(coverage),'entre_rios_2001_departamentos':len(manifest),'entre_rios_2001_filas_fuerza':len(combined),'datar_filas':len(x),'datar_cobertura':{str(k):{'filas':len(g),'distritos':g.provincia.nunique(),'unidades_territoriales':len(g[['provinciaId','departamentoId']].drop_duplicates())} for k,g in x.groupby('eleccion')},'polar_filas_mesa':len(p),'polar_distritos':p.codprov.nunique(),'polar_departamentos':len(a),'polar_mesas_superan_electores':int(flag.sum()),'polar_votos_suma':int(p.votos_suma.sum())}
(root/'diagnostico.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=False,indent=2))
