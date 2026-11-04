"""Códigos y nombres desde resultados oficiales; no se usan mesas para unir años."""
from pathlib import Path
import concurrent.futures as cf
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

def extraer(year):
 out=HERE/f'nombres_{year}.pkl'
 if out.exists():return pd.read_pickle(out)
 files=[f for f in (ROOT/'datos_oficiales'/str(year)/'x').rglob('*.csv') if 'result' in f.name.lower() and '__MACOSX' not in str(f)]
 assert len(files)==1,files
 cols=['distrito_id','seccion_id','seccion_nombre','circuito_id','circuito_nombre']
 chunks=[]
 for ch in pd.read_csv(files[0],dtype=str,usecols=cols,chunksize=1500000):
  chunks.append(ch.drop_duplicates())
 t=pd.concat(chunks).drop_duplicates().reset_index(drop=True)
 t['distrito_id']=t.distrito_id.astype(int).map('{:02d}'.format)
 t['seccion_id']=t.seccion_id.astype(int)
 t['circuito_id']=t.circuito_id.str.upper().str.strip().str.lstrip('0').replace('','0')
 t.to_pickle(out);t.to_csv(out.with_suffix('.csv'),index=False,encoding='utf-8-sig')
 print('NOMBRES',year,len(t),flush=True)
 return t
if __name__=='__main__':
 with cf.ThreadPoolExecutor(3) as pool:list(pool.map(extraer,[2019,2023,2025]))
