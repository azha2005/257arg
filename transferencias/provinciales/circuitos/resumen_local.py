import json
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
H=Path(__file__).resolve().parent
if __name__=='__main__':
 j=json.loads((H/'fuentes/corrientes_filtro_circuito.json').read_text(encoding='utf8'))
 print('FILTROS',[(x['filtroTipoId'],x['descripcion'],len(x['datos'])) for x in j])
 print('CIR SAMPLE',next(x for x in j if x['filtroTipoId']==4)['datos'][:5])
 d=pd.read_pickle(ROOT/'transferencias/provinciales2025/fuentes/sf_primarias2025.pkl')
 print('SF CAPITAL',d[d.nomsec.str.contains('CAPITAL')][['circuito','nomcir']].drop_duplicates().to_dict('records'))
 print('RAW DINE',list((ROOT/'datos_oficiales/2025/x').glob('*.csv')))
 for file in (ROOT/'datos_oficiales/2025/x').glob('*esult*.csv'):
  print('COLS',pd.read_csv(file,nrows=1).columns.tolist())
 d=pd.read_pickle(ROOT/'transferencias/provinciales2023/salta_detalle.pkl')
 v=d[d['Categoría'].eq('GOBERNADOR')]
 print('SALTA2023',v.Lista.unique().tolist(),'subcircs',v.Subcircuito.nunique(),'nulos',v[v.Subcircuito.isna()].Votos.sum())
