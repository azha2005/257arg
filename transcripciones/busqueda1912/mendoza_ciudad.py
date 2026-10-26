"""Lectura visual de 45 mesas; sólo resoluciones últimas del acta, sin rellenar residuos."""
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent
# mesa|PDF|acta|sobres|Benegas|Gaviola|blancos expresos|impugnados expresos|otros candidatos
RAW='''1|7,9|152|151|117|33|1||
2|9|150|150|115|31|4||
3|9|153|153|108|40|4||Pedro N. Ortiz:1
4|9,11|132|132|87|42|3||
5|11|152|152|114|35|1||Salvador Segura B.:1;Eduardo Flores:1
6|11|132|132|102|30|1||
7|11|149|150|114|34|1||Ricardo Báez:1
8|11,13|146|145|103|40|1||Salvador Segura B.:1
9|13,19,33,35,37,39,41,43|147|147|114|33|||
10|15|136|137|109|28|||
11|15|147|147|108|39|||
12|15|142|142|93|45|1|1|Pedro N. Ortiz:2
13|15,17|154|153|109|43|||Ricardo Báez:1
14|17|145|145|94|50||1|
15|17|147|147|110|35|2||
16|17|154|154|111|36|||
17|17|148|145|98|43|3||Pedro N. Ortiz:1
18|17,19|138|139|103|36|||
19|21|130|130|98|29|2||Domingo Astorga:1
20|21|144|143|107|36|||
21|21|207|207|162|39|3||José N. Lencinas:1;Abelardo Gudiño:1;Salvador B. Reta:1
22|21,23|146|146|116|28|||Carlos Alurralde:1;Nicolás D. Guida:1
23|23|148|148|114|33|1||
24|23,41,43|118|122|85|36|||Salvador Segura B.:1
25|23,25|117|117|89|27|||Pedro N. Ortiz:1
26|25|133|132|94|35|||Salvador Segura B.:2;Pedro N. Ortiz:1
27|25|141|141|99|38|||Pedro N. Ortiz:3;José Antonio Delgado:1
28|25|136|136|95|39|1||José A. Delgado:1
29|25,41,43|137|140|110|29|1||
30|27|140|140|108|29|1||Ricardo Báez:1
31|27|144|144|115|22|||José A. Delgado:3;Pedro N. Ortiz:4
32|27|125|125|93|29|2||José A. Delgado:1
33|27,41,43,45|146|143|91|44|3||Pedro N. Ortiz:1;Julián Barraquero:1;Pedro T. Lucero:1;Juan Videla Cuello:1;Emiliano Torres:1
34|27|152|152|123|28|||José M. Usandivaras:1
35|27,29|145|145|108|37|||
36|29|125|125|96|27|1||José N. Lencinas:1
37|29|108|108|80|27|1||
38|29|140|140|101|33|1||Pedro N. Ortiz:1;Julián Barraquero:1;José Palma:1;Arturo Funes:1;Agustín Leiva:1
39|29|124|124|93|28|3||
40|29|115|115|77|38|||
41|29,31|137|137|99|37|1||
42|31|141|141|103|34|4||
43|31|125|125|99|26|||
44|31|122|122|91|27|2||Ricardo Villanueva:1;José N. Lencinas:1
45|31|98|98|68|28|2||'''
NOTES={
1:'Acta 152, urna 151; dos tarjetas a favor de Gaviola aceptadas por mayoría; 117 y 33 son el cómputo explícito.',
6:'La fuente imprime 102 Benegas y 30 Gaviola, un sobre vacío y una tarjeta a Gaviola computada por la Junta. No se suma otra unidad por interpretación; los valores explícitos más el blanco exceden sobres en 1.',
9:'Primero anulada en PDF 13; reconsiderada y aprobada en PDF 41; cómputo 114/33 en PDF 43. El acta final allí dice 147; en el examen inicial se leía 145.',
10:'Acta 136; columna votó y urna 137. La Junta admite 137.',
12:'Un voto impugnado y un sobre vacío, además de candidatos explícitos.',
14:'Un voto impugnado explícito.',
16:'Candidatos publicados suman 147 frente a 154 sobres; residuo de 7 SIN imputar a blancos ni a otros.',
17:'148 en acta; 145 sobres. La fuente explica las tres anotaciones erróneas.',
18:'Acta y registro 138; urna 139. Admitida por mayoría con 103/36.',
20:'Acta 144; urna 143. Nombre repetido en registro.',
24:'Acta 118, columna votó 119, urna 122; aprobada en PDF 41 y cómputo 85/36/1 en PDF 43.',
26:'Acta 133; urna 132; registros con numeración repetida.',
29:'Acta 137, urna 140. La Junta excluye una boleta suelta y otro voto sin libreta; publica 110/29 y un sobre vacío. La relación entre exclusión y total de sobres queda dudosa; se conservan cifras expresas.',
30:'108+29+1 candidato menor+1 blanco=139, frente a 140 sobres: diferencia -1 sin corregir.',
33:'Acta 146, registros 142/141, urna 143; admitida PDF 41 y escrutada PDF 43-45.',
45:'La fuente imprime veintiocho (sic) para Gaviola; se conserva 28.'}
def build():
    controls=[];long=[]
    for line in RAW.splitlines():
        m,pages,a,s,b,g,w,imp,other=line.split('|');m=int(m)
        values={'Pedro Benegas':int(b),'Estanislao D. Gaviola':int(g)}
        if other:
            for item in other.split(';'):
                name,value=item.rsplit(':',1);values[name]=int(value)
        subtotal=sum(values.values())+(int(w) if w else 0)+(int(imp) if imp else 0)
        controls.append(dict(mesa=m,paginas_pdf=pages,votantes_acta=a,sobres=s,benegas=b,gaviola=g,blancos_expresos=w,impugnados_expresos=imp,otros_json=json.dumps({k:v for k,v in values.items() if k not in ['Pedro Benegas','Estanislao D. Gaviola']},ensure_ascii=False),suma_cifras_expresas=subtotal,diferencia_menos_sobres=subtotal-int(s),nota=NOTES.get(m,'Cómputo explícito de la Junta; blanco vacío significa no informado, no cero.')))
        for name,value in values.items():long.append(dict(provincia='Mendoza',unidad_fuente='Ciudad de Mendoza',mesa=m,candidato=name,votos=value,paginas_pdf=pages,fuente_id='42-d-1912',nota=NOTES.get(m,'Transcripción visual del resultado explícito; consulta 2026-10-15.')))
    for name,rows in [('mendoza_ciudad_mesas_controles.csv',controls),('mendoza_ciudad_mesas_candidatos.csv',long)]:
        with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    assert {r['mesa'] for r in controls}==set(range(1,46))
    totals={n:sum(r['votos'] for r in long if r['candidato']==n) for n in ['Pedro Benegas','Estanislao D. Gaviola']}
    print(json.dumps(dict(mesas=len(controls),totales_candidatos=totals,sobres=sum(int(r['sobres']) for r in controls),votantes_acta=sum(int(r['votantes_acta']) for r in controls),discrepancias=[r for r in controls if r['diferencia_menos_sobres']]),ensure_ascii=False,indent=2))
    return totals
if __name__=='__main__':build()
