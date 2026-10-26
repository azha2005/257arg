"""Búsqueda acotada, de sólo lectura, en el inventario de planillas del usuario."""
from pathlib import Path
import json, pandas as pd
ROOT=Path(__file__).resolve().parent
inventory=json.loads((ROOT/'mapa2009/busqueda_fuentes/busqueda_planillas_2009.json').read_text(encoding='utf8'))
result=[]
for x in inventory:
    p=Path(x['path'])
    selected=[]
    for s in x.get('sheets',[]):
        head=str(s.get('head',[]))
        if ('anio' in head and 'eleccion' in head) or ('2003' in p.name and 'presi' not in p.name.lower()) or ('2005' in p.name):selected.append(s['sheet'])
    if not selected:continue
    rec={'path':str(p),'sheets':[]}
    for sh in selected:
        try:
            df=pd.read_excel(p,sheet_name=sh)
            r={'sheet':sh,'rows':len(df),'columns':list(map(str,df.columns))[:14]}
            if {'anio','eleccion'}<=set(df):r['elecciones']={str(k):int(v) for k,v in df.groupby(['anio','eleccion']).size().items()}
            rec['sheets'].append(r)
        except Exception as e:rec['sheets'].append({'sheet':sh,'error':str(e)})
    result.append(rec)
(ROOT/'busqueda_complementos_2003_2025.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
