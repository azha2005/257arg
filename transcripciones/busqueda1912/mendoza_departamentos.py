"""Cifras expresas del 42-D; blancos/ceros ausentes nunca se rellenan por residuo."""
from pathlib import Path
import csv,json,collections
import mendoza_ciudad
P=Path(__file__).resolve().parent
# mesa|PDF|acta|sobres|Benegas|Gaviola|blancos expresos|impugnados excluidos|otros
# Una mesa repetida en la narrativa se representa una sola vez, con el último cómputo.
RAW='''@San Rafael
1|45|119|120|84|35|1||
2|45|119|120|78|39|3||
3|45|77|78|48|29|1||
4|45,47|123|124|76|45|2||José A. Salas:1
5|47|118|118|87|30|1||
6|47|124|125|74|51|||
7|47|137|137|89|47|1||
8|47,49|120|120|77|43|||
9|49|79|80|50|29|1||
10|49|95|99|67|32|||
11|49|101|104|72|30|2||
12|51|107|107|75|32|||
13|51|102|102|71|27|4||
14|51|129|129|49|78|2||
15|51|143|148|44|100|3|1|
16|51|77|77|38|36|2||José A. Salas:1
17|53|86|87|12|74|1||
18|53|68|68|10|56|2||
19|53|44|43|10|33|||
20|53|81|81|21|60|||
21|53|63|65|14|50|1||
22|53|78|78|36|41|1||
23|53|54|55|17|38|||
24|53,55|||53|28|4||Alberto Herrero:1
@Lavalle
1|55|156|156|98|54|1|3|
2|55|131|129|93|36|||
3|55|68|69|46|23|||
4|55|||100|12|||
5|55,57|||72|31|3||
6|57|||43|106|5||
7|57|214|215|57|153|5||
8|57|||0|102|||
9|57|101|102||101|1||
@Tupungato
1|57|||65|96|4||
2|57,59|164|178|57|112|1||
@Tunuyán
1|59|||64|112|1||
2|59|153|152|86|63|3||
3|59,61|153|153|68|82|3||
4|61|120|124|91|29|||
5|61|181|182|85|94|3||
@San Carlos
1|61,97,101,103|42|42|36|2|4||
2|61|||106|21|2||
3|63|147|148|48|99|1||
4|63|206|207|67|139|1||
@Rivadavia
1|63|137|138|73|65|||
2|63|||85|58|||
3|63|||99|65|2||
4|63,65|151|149|103|46|||
5|65|145|146|61|84|1||
6|65|156|158|57|100|1||
7|65|||57|85|2||
8|65|||74|54|1||
9|65|165|168|45|121|2||
10|65,67|144|145|83|62|||
11|67|128|131|78|52|1||
@Luján
1|67|||75|76|2||
2|67|150|151|73|78|||
3|67|160|160|112|43|5||
4|67|151|152|55|95|2||
5|69|139|140|54|85||1|
6|69|155|146|65|77|4||
7|69|152|152|62|87|3||
8|69|155|154|77|75|2||
9|69|156|156|86|68|2||
10|69,71|206|205|116|88|1||
11|71|157|157|54|103|||
12|71||127|87|37|3||
13|71|65|65|20|45|||
@Santa Rosa
1|71|191|191|161|29|1||
2|71|143|143|116|25|2||
3|71,73|158|158|79|77|2||
4|73|135|135|104|31|||
5|73|82|82|46|35|||
@La Paz
1|73|143|143|96|46|1||
2|73|140|141|102|34|5||
3|73|149|152|109|43|||
4|73|131|130|83|46|1||
5|75|33|33|20|13|||
6|75|70|70|41|29|||
@Junín
1|75|151|151|52|98|1||
2|75|146|146|64|81|1||
3|75|215|215|125|83|6||José A. Delgado:1
4|75|162|161|132|27|2||
5|75|148|150|123|27|||
6|75,77|159|159|137|22|||
7|77|100|100|88|12|||
8|77|128|128|82|46|||
@San Martín
1|77|146|146|111|35|||
2|77|140|141|104|36|1||
3|77|91|91|76|13|2||
4|77,79|157|155|105|49|1||
5|79|213|215|173|41||1|
6|79,97,101,103|38|38|34|3|||Joaquín Guevara:1
7|79,97,101|||||||
8|79|146|146|114|30|2||
9|79|140|143|64|77|2||
10|81|109|109|65|42|2||
11|81|145|148|89|56|3||
12|81|136|136|103|30|4||
13|81,97,101,103|8|8|7|1|||
14|81,97,101,103|6|6|6|0|||
@Las Heras
1|83|149|149|127|21|1||
2|83|150|158|120|35|3||
3|83|162|161|113|47|1||
4|83|149|149|111|38|||
5|83|143|144|113|29|2||
6|83,85|169|169|135|33|1||
7|85|80|80|63|17|||
@Guaymallén
1|85|153|156|103|53|||
2|85|142|142|90|51|1||
3|85|144|142|105|37|2||
4|85|148|146|98|47|||Julio E. Ducómb:1
5|85,97,99,101,103|14|14|6|1|||José N. Lencinas:6;Vicente Villegas:1
6|85,87|157|158|135|21|1||
7|87,97,101,103|6||0|0|6||
8|87,97,101,103|4||0|0|4||
9|87|153|154|137|15|2||
10|87|136|137|122|14|1||
11|89|124|125|83|42|||
@Godoy Cruz
1|89|164|166|137|29|||
2|89|157|157|123|34|||
3|89|147|150|114|35|||
4|89|155|155|123|31|1||
5|89|169|167|122|43|2||
6|89,91|163|163|120|39|1||Pedro N. Ortiz:1;J. Edecio Correa:1;Enrique A. Pontis:1
7|91|151|151|124|27|||
8|91|150|150|112|35|3||
9|91|171|171|128|42|1||
@Maipú
1|91|126|126|108|18|||
2|91,93|134|134|107|27|||
3|93|144|144|123|21|||
4|93|140|141|111|28|||Pedro N. Ortiz:2
5|93|146|145|123|19|3||
6|93|144|143|115|25|2||Pedro N. Ortiz:1
7|93,95|155|156|120|32|2||Pedro N. Ortiz:2
8|95|155|154|118|35|1||
9|95|148|148|104|44|||
10|95|156|158|128|29|1||
11|95,97,99,103|7|7|7|0|||
12|97|113|116|60|30|||
13|97,99,103|22|22|12|10|||
14|97,99,103,105|49|49|47||1||Domingo Astorga:1
15|97|145|148|67|81|||'''

def build():
    controls=[];long=[];unit='Ciudad de Mendoza'
    records=[(unit,line) for line in mendoza_ciudad.RAW.splitlines()]
    for line in RAW.splitlines():
        if line.startswith('@'):unit=line[1:]
        else:records.append((unit,line))
    for unit,line in records:
        mesa,pages,a,s,b,g,w,imp,other=line.split('|')
        note='Lectura visual 2026-10-15; cifra vacía = no expresa en fuente, nunca cero ni residuo. Fecha original 7/4; donde hubo anulación se usa la complementaria de 28/4, escrutada 30/4.'
        comp=(unit=='San Carlos' and mesa=='1') or (unit=='San Martín' and mesa in ['6','7','13','14']) or (unit=='Guaymallén' and mesa in ['5','7','8']) or (unit=='Maipú' and mesa in ['11','13','14'])
        if comp:note+=' Mesa COMPLEMENTARIA; sólo último escrutinio, no se suma la votación anulada.'
        if unit=='San Martín' and mesa=='7':note+=' La mesa 7 fue anulada y convocada de nuevo; no se encontró su cómputo en la enumeración final PDF 103. Pendiente, no cero.'
        if unit=='Lavalle' and mesa=='8':note+=' Cero Benegas respaldado por la frase de que los 102 votos de esta mesa correspondieron a Gaviola.'
        if unit=='Lavalle' and mesa=='9':note+=' Sólo se publica cifra para Gaviola; Benegas queda sin cifra expresa.'
        if unit=='Maipú' and mesa=='14':note+=' Distribución publicada: Benegas 47, Astorga 1 y blanco 1; Gaviola no tiene cifra expresa.'
        if unit=='Ciudad de Mendoza':note+=' '+mendoza_ciudad.NOTES.get(int(mesa),'')
        candidates={}
        for name,value in [('Pedro Benegas',b),('Estanislao D. Gaviola',g)]:
            if value!='':candidates[name]=int(value)
        if other:
            for item in other.split(';'):
                name,value=item.rsplit(':',1);candidates[name]=int(value)
        subtotal=sum(candidates.values())+(int(w) if w else 0)+(int(imp) if imp else 0)
        controls.append(dict(unidad_fuente=unit,mesa=int(mesa),paginas_pdf=pages,fecha_comicio='28/4/1912' if comp else '7/4/1912',votantes_acta=a,sobres=s,benegas=b,gaviola=g,blancos_expresos=w,impugnados_expresos=imp,otros_json=json.dumps({n:v for n,v in candidates.items() if n not in ['Pedro Benegas','Estanislao D. Gaviola']},ensure_ascii=False),suma_cifras_expresas=subtotal,diferencia_menos_sobres=subtotal-int(s) if s else '',nota=note))
        for name,value in candidates.items():
            long.append(dict(provincia='Mendoza',unidad_fuente=unit,mesa=mesa,candidato=name,votos=value,paginas_pdf=pages,fecha_comicio='28/4/1912' if comp else '7/4/1912',fuente_id='42-d-1912',nota=note))
    assert len({(r['unidad_fuente'],r['mesa']) for r in controls})==len(controls)
    totals=[]
    for unit in dict.fromkeys(r['unidad_fuente'] for r in controls):
        c=[r for r in controls if r['unidad_fuente']==unit]
        for name,col in [('Pedro Benegas','benegas'),('Estanislao D. Gaviola','gaviola')]:
            vals=[r[col] for r in c if r[col]!='']
            totals.append(dict(unidad_fuente=unit,candidato=name,suma_cifras_expresas=sum(map(int,vals)),mesas_registradas=len(c),mesas_con_cifra=len(vals),mesas_sin_cifra=';'.join(str(r['mesa']) for r in c if r[col]==''),completo_candidato=len(vals)==len(c),nota='Suma sin imputación. No certifica ausencia de errores internos del original ni cierre provincial.'))
    for file,rows in [('mendoza_mesas_candidatos.csv',long),('mendoza_mesas_controles.csv',controls),('mendoza_totales_territoriales.csv',totals)]:
        with (P/file).open('w',encoding='utf-8-sig',newline='') as f:
            wri=csv.DictWriter(f,fieldnames=list(rows[0]));wri.writeheader();wri.writerows(rows)
    sums={n:sum(r['suma_cifras_expresas'] for r in totals if r['candidato']==n) for n in ['Pedro Benegas','Estanislao D. Gaviola']}
    report=dict(unidades=len(set(r['unidad_fuente'] for r in controls)),mesas=len(controls),sumas_expresas=sums,total_acta_pdf105={'Pedro Benegas':15833,'Estanislao D. Gaviola':8247},diferencias={n:sums[n]-v for n,v in [('Pedro Benegas',15833),('Estanislao D. Gaviola',8247)]},faltantes=[r for r in totals if not r['completo_candidato']],mesas_con_diferencia_aritmetica=[{k:r[k] for k in ['unidad_fuente','mesa','paginas_pdf','diferencia_menos_sobres']} for r in controls if r['sobres'] and r['diferencia_menos_sobres']!=0])
    report['candidatos_menores']={'suma_recuperada':sum(r['votos'] for r in long if r['candidato'] not in ['Pedro Benegas','Estanislao D. Gaviola']),'total_acta_pdf105':74,'nota':'Diferencia -4 no imputada. Las grafías de nombres se conservan; no se certifica número de personas distintas.'}
    report['interpretacion_diferencias']='La lista aritmética no implica que todos sean errores: Tupungato 2 excluye 8 sobres, Tunuyán 4 excluye 4 y Maipú 12 anula votos de personas añadidas indebidamente (rango 126-151). Esas exclusiones explican los déficits -8, -4 y -26; no se agregan a votos de candidatos ni blancos.'
    (P/'mendoza_cotejo_provincial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return totals
if __name__=='__main__':build()
