"""Inventario de cruces y reproducción de la selección territorial guardada."""
from pathlib import Path
import json
import re
import pandas as pd
import estimar as e

HERE=Path(__file__).resolve().parent
OUT=HERE/'revision_cacopardo_1967'
PROFILES=[(.75,1.33),(.6,2.3),(.6,2.7),(.5,2.),(.6,2.),(.5,2.3),(.4,2.5)]

def argument(value):return value if re.search('[a-z]$',value) else int(value)

def main():
    OUT.mkdir(exist_ok=True)
    result=[]
    for folder in sorted(HERE.iterdir()):
        path=folder/'control.json'
        if not folder.is_dir() or not re.fullmatch(r'\d{4}[a-z]*_\d{4}[a-z]*',folder.name) or not path.exists():continue
        ctl=json.loads(path.read_text(encoding='utf8'))
        row=dict(par=folder.name,usados_guardados=ctl.get('usados'),estado='sin perfil reproducible')
        old=e.RATIO
        try:
            a,b=map(argument,folder.name.split('_'))
            profiles=[tuple(ctl['filtro_razon_crecimiento'])]+PROFILES if 'filtro_razon_crecimiento' in ctl else PROFILES
            for profile in profiles:
                e.RATIO=profile
                A,B,*_,fresh=e.prepare(a,b)
                checks=[fresh.get(k)==ctl.get(k) for k in ('usados','electores_origen_usados','electores_destino_usados')]
                if all(checks):
                    row.update(estado='selección reproducida',ratio_min=profile[0],ratio_max=profile[1],
                               distritos=len(fresh['unidades_por_provincia']),comunes=fresh['comunes'])
                    if 'marginal_origen' in ctl:
                        row['marginales_coinciden']=ctl['marginal_origen']==A.sum().astype(int).to_dict() and ctl['marginal_destino']==B.sum().astype(int).to_dict()
                    break
        except Exception as exc:row.update(estado='requiere revisión',error=str(exc))
        finally:e.RATIO=old
        result.append(row)
    pd.DataFrame(result).to_csv(OUT/'inventario_selecciones.csv',index=False,encoding='utf-8-sig')
    (OUT/'inventario_selecciones.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(pd.DataFrame(result).to_string(index=False))

if __name__=='__main__':main()
