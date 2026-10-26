"""Comparación candidato a candidato: diario 25/4 frente a diploma 29/4."""
from pathlib import Path
import csv
P=Path(__file__).resolve().parent
data=list(csv.DictReader((P/'santa_fe_provincial_25abril.csv').open(encoding='utf-8-sig')))
primary={'Rogelio Araya':36747,'Benjamín Ábalos':36513,'Miguel Coronado':36147,'Francisco G. Valdez':35855,'Víctor Pesenti':17856,'Lisandro de la Torre':17630}
out=[]
for r in data:
    if r['candidato'] in primary:
        value=primary[r['candidato']]
        r['nota']='Crónica 25/4, anterior al cierre de Junta del 26/4 y al diploma de 29/4. Comparar mismo candidato en santa_fe_cotejo_diploma.csv; no armonizar ni sustituir el diario.'
        out.append(dict(candidato_diario=r['candidato'],votos_diario_25abril=r['votos'],votos_diploma_29abril=value,diferencia_diario_menos_diploma=int(r['votos'])-value,fuente_diario='santa-fe-6514',fuente_diploma='17-d-1912',fila_fuente_diploma='PDF 3, carta/diploma 29/4/1912',nota='Lectura visual del diploma y crónica; Ábalos/Ávalos conservan variante nominal. Diferencias no repartidas territorialmente.'))
for name,items in [('santa_fe_provincial_25abril.csv',data),('santa_fe_cotejo_diploma.csv',out)]:
    with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
print('Comparados',len(out),'candidatos; no hay votos departamentales nuevos.')
