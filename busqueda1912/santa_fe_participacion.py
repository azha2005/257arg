"""Cuadro nacional del diario Santa Fe, 16/4/1912, p. 2; lectura visual."""
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent
RAW='''La Capital|10299|8106|2193|50
Rosario|22571|18212|4359|111
9 de Julio|1621|413|1208|8
San Justo|2054|1623|431|10
Las Colonias|5255|4476|779|28
San Lorenzo||2912|112|15
General López|8516|5971|2545|44
Vera|7008|3545|3463|35
Belgrano|2006|1684|322|10
San Cristóbal|3606|2175|1431|17
Constitución|4009|3461|548|20
Iriondo|3734|3248|486|19
Castellanos|4135|3505|630|21
Caseros|3551|2959|592|17
San Gerónimo|4290|3782|508|22
General Obligado|5838|3601|2257|30
San Martín|3061|2562|499|14
San Javier|1954|1605|349|9
Garay|1539|1038|501|8'''
def build():
    rows=[]
    for line in RAW.splitlines():
        name,ins,vot,no,mesas=line.split('|')
        note='Cuadro de participación para diputados nacionales; no contiene votos por candidato. Consulta y lectura visual 2026-10-15.'
        if name=='San Lorenzo':note+=' Inscriptos de lectura insegura (3?24): se deja vacío, no se reconstruye mediante suma.'
        if name=='General Obligado':note+=' No sufragantes se lee 2257; con inscriptos 5838 y sufragantes 3601 no cierra. Conservar sin corregir.'
        rows.append(dict(provincia='Santa Fe',departamento=name,inscriptos=ins,sufragantes=vot,no_sufragantes=no,mesas=mesas,diferencia_ins_menos_sufragantes_y_no=int(ins)-int(vot)-int(no) if ins else '',fuente_id='santa-fe-6508',fila_fuente='16/4/1912, p. 2, Cómputo general de sufragantes, '+name,nota=note))
    with (P/'santa_fe_participacion_1912.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    sums={k:sum(int(r[k]) for r in rows if r[k]) for k in ['inscriptos','sufragantes','no_sufragantes','mesas']}
    report=dict(totales_impresos=dict(inscriptos=98371,sufragantes=74878,no_sufragantes=23493,mesas=488),suma_filas_con_valor=sums,inscriptos_filas_numericas=18,nota='La suma parcial de inscriptos no es comparable directamente al total: falta una lectura. Diferencias no corregidas.')
    (P/'santa_fe_participacion_controles.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
