"""Custodia de resultados: no imprime ni entrega el total de PASO 2021 al predictor."""
from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,datetime
from config import KEY,FORCES,block
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'permitidos';OUT.mkdir(exist_ok=True)
VAULT=HERE/'sellado';VAULT.mkdir(exist_ok=True)

def build(y):
 dest=VAULT/'mesas_2021paso.pkl' if y=='2021_paso' else OUT/('mesas_'+y+'.pkl')
 if dest.exists():return
 source=next((ROOT/'datos_oficiales'/y/'x').rglob('*Resultado*.csv'))
 parts=[];names=set()
 use=['eleccion_tipo','recuento_tipo','distrito_id','seccion_id','circuito_id','mesa_id','mesa_tipo','mesa_electores','cargo_nombre','agrupacion_nombre','votos_tipo','votos_cantidad']
 for ch in pd.read_csv(source,usecols=use,dtype=str,chunksize=750000,low_memory=False):
  ch=ch[ch.cargo_nombre.fillna('').str.upper().str.contains('DIPUTAD.*NACIONAL')].copy()
  if ch.empty:continue
  expected='PASO' if y=='2021_paso' else 'GENERAL'
  if not ch.eleccion_tipo.str.upper().str.startswith(expected).all():raise ValueError('Tipo de elección inesperado')
  ch=ch[ch.mesa_tipo.str.upper().str.startswith('NATIVO')].copy()
  ch['mesa_tipo']='NATIVOS'
  ch['distrito_id']=ch.distrito_id.astype(int).map('{:02d}'.format)
  ch['seccion_id']=ch.seccion_id.astype(int)
  ch['circuito']=ch.circuito_id.fillna('').str.strip().str.upper().str.lstrip('0').replace('','0')
  ch['mesa_id']=ch.mesa_id.astype(str).str.strip().str.lstrip('0').replace('','0')
  ch['e']=pd.to_numeric(ch.mesa_electores,errors='raise').fillna(0)
  ch['v']=pd.to_numeric(ch.votos_cantidad,errors='raise')
  t=ch.votos_tipo.str.upper().fillna('')
  ch['col']=np.where(t.str.startswith('POSITIVO'),ch.agrupacion_nombre.map(lambda n:block(n,y)),np.where(t.str.contains('BLANCO'),'BLANCO',np.where(t.str.contains('NULO'),'NULO','OTROS')))
  names.update((d,str(n).strip(),block(n,y)) for d,n in ch.loc[t.str.startswith('POSITIVO'),['distrito_id','agrupacion_nombre']].drop_duplicates().itertuples(index=False,name=None))
  parts.append(ch.groupby(KEY+['e','col']).v.sum())
 s=pd.concat(parts).groupby(level=list(range(len(KEY)+2))).sum()
 w=s.unstack('col',fill_value=0).reset_index()
 w=w.groupby(KEY,as_index=False).agg({c:'max' if c=='e' else 'sum' for c in w if c not in KEY})
 for c in FORCES+['BLANCO','NULO','OTROS']:
  if c not in w:w[c]=0
 w.columns.name=None
 w=w[w.e>0].reset_index(drop=True)
 if not set(w.distrito_id).issubset({f'{i:02d}' for i in range(1,25)}):raise ValueError('Distritos no territoriales')
 w.to_pickle(dest)
 pd.DataFrame(sorted(names),columns=['distrito','nombre','bloque']).to_csv(HERE/('mapeo_'+y+'.csv'),index=False,encoding='utf-8-sig')
 frame=w[KEY+['e']].copy()
 frame.to_pickle(OUT/('marco_'+y+'.pkl'))
 # Disponibilidad solo dice que se recibió algún voto; no aporta preferencia partidaria.
 ready=(w[FORCES+['BLANCO','NULO','OTROS']].sum(1)>0).to_numpy()
 np.save(OUT/('disponibilidad_'+y+'.npy'),ready)
 meta={'eleccion':y,'fuente':str(source.relative_to(ROOT)),'sha256_fuente':hashlib.sha256(source.read_bytes()).hexdigest(),'mesas_marco':len(w),'actas_disponibles':int(ready.sum()),'distritos':len(w.distrito_id.unique()),'sha256_tabla':hashlib.sha256(dest.read_bytes()).hexdigest(),'generado_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (HERE/('fuente_'+y+'.json')).write_text(json.dumps(meta,indent=2),encoding='utf8')
 print(y,'preparado; claves/electores y disponibilidad separados de votos',flush=True)

if __name__=='__main__':
 for y in ['2013','2015','2017','2019','2021_paso']:build(y)
