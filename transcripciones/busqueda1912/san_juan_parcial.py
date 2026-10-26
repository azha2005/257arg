"""Mesas explícitas de Angaco Norte/Sur y complementaria de Calingasta; no convierte candidatos a listas."""
from pathlib import Path
import csv,json,collections
P=Path(__file__).resolve().parent
# unidad|mesa|PDF|sufragantes|Echegaray|Albarracín|Brandam|Cano|sobres/votos en blanco expresos
RAW='''Angaco Sud|1|63|168|112|112|53|53|3
Angaco Sud|2|63,64|169|99|100|64|65|4
Angaco Sud|3|64|187|111|111|71|71|3
Angaco Sud|4|64|136|78|78|53|53|2
Angaco Norte|1|65|177|117|117|59|59|
Angaco Norte|2|65,66|174|81|81|92|92|1
Angaco Norte|3|66|172|90|90|79|79|3
Angaco Norte|4|66|180|88|88|92|92|
Calingasta|única complementaria|76,77|205|123|121|79|84|
Caucete|1|67|168|111|111|56|56|1
Caucete|2|67|169|72|72|95|95|2
Caucete|3|68,73,74|184|86|86|97|97|1
Caucete|4|68|175|92|90|81|81|2
Caucete|5|68|146|81|80|63|63|2
Caucete|6|68,69|164|71|71|90|90|3
Caucete|7|69|170|79|79|81|81|
Caucete|8|69|186|96|96|90|90|
Veinticinco de Mayo|1|69,70,73,74,75|184|40|40|121|121|2
Veinticinco de Mayo|2|70|167|43|43|122|122|1
Veinticinco de Mayo|3|70|87|45|44|42|42|
Pampa del Chañar|1|57|180|61|61|111|111|10
Pampa del Chañar|2|57,58|160|56|56|103|103|1
Pampa del Chañar|3|58|174|53|53|116|114|5
Pampa del Chañar|4|58|162|60|60|102|102|1
Pampa del Chañar|5|58|198|58|58|140|140|
Barreal|única|59|126|85|85|40|40|
Mogna|única complementaria|55,76,77|174|136|136|27|27|
Pocito|6 complementaria|45,50,76,77,78|178|115|115|63|63|
Albardón|1|60,61|172|83|83|89|89|
Albardón|2|61|178|81|81|86|86|
Albardón|3|61,62|151|73|73|73|73|5
Albardón|4|62|178|108|108|66|66|4
Albardón|5 y fracción|62,63|210|119|118|91|92|
Albardón|6|63|130|56|55|74|74|
Huaco|1|53|172|86|86|84|84|2
Huaco|2|53,54|132|76|76|41|41|2
Villa de Jáchal|1|52|173|113|113|56|56|4
Villa de Jáchal|2|52|175|113|119|48|50|1
Villa de Jáchal|3|52|174|103|103|69|69|1
Villa de Jáchal|4|52,53|109|103|103|4|4|2
Pampa Vieja|única|53|244|147|147|92|92|4
Valle Fértil|1|49,50|154|59|59|92|92|2
Valle Fértil|2|51|164|63|63|100|100|
Rodeo|2|49|167|51|51|116|116|
Rodeo|3|49|103|43|43|60|60|
Iglesia|1|48|168|84|84|79|79|5
Iglesia|2|48|103|34|34|68|68|1
Rodeo|1|48,49|167|57|57|110|110|
Cieneguita|única|47|118|28|28|90|90|
Retamito|única|48|108|64|64|44|44|
Astica|única|51|109|43|43|66|66|
Los Berros|única|46||37|37|90|90|4
Cochagual|1|45||55|55|118|118|3
Cochagual|2|45,46||28|28|53|53|1
Pocito|1|42||96|95|72|73|1
Pocito|2|44||73|73|100|100|3
Pocito|3|44||86|86|92|92|
Pocito|4|44||94|94|86|86|3
Pocito|5|44,45||116|115|53|54|6
Santa Lucía|1|40,41||73|73|88|90|3
Santa Lucía|2|41||111|104|70|75|1
Santa Lucía|3|41||135|134|43|42|1
Santa Lucía|4|41||76|76|73|73|3
Alto de Sierra|única|41,42||155|155|62|62|3
Nueve de Julio|única|42||35|32|97|100|1
Trinidad|1|37||91|93|73|86|1
Trinidad|2|37||94|90|82|86|
Trinidad|3|37,39||103|107|71|77|1
Trinidad|4|37,38||101|90|77|78|1
Trinidad|5|38||95|89|70|76|2
Trinidad|6|38||97|93|71|73|6
Trinidad|7|38,39||116|111|68|75|
Rivadavia|1|34,35||118|119|25|25|1
Rivadavia|2|35||99|99|70|70|5
Rivadavia|3|35||27|27|83|83|1
Desamparados|5|33,34||97|96|83|83|
Desamparados|6|34||78|76|86|87|2
Desamparados|7|34||101|101|66|66|
Desamparados|8|34,35||95|95|90|90|1
Desamparados|1|30,31||89|89|94|94|3
Desamparados|2|31||110|109|72|72|1
Desamparados|3|31||72|72|103|103|1
Desamparados|4|31||85|84|79|80|2
Concepción|1|20,21|186|82|81|100|100|4
Concepción|2|21|185|101|98|86|83|1
Concepción|3|21,22|167|75|71|93|91|2
Concepción|4|21,22,26,27|172|87|88|83|83|2
Concepción|5|22|183|82|81|96|94|5
Concepción|6|24,26,28|184|96|96|86|86|
Concepción|7|24,26,28|168|92|90|83|82|2
Concepción|8|24,30|179|71|71|107|107|1
Concepción|9|24,30|74|33|33|41|41|
Chimbas|única|25|271|108|107|156|157|
Capital - Primer Distrito|1|5,6,7|164|94|97|62|65|
Capital - Primer Distrito|2|7,8|161|77|72|79|79|1
Capital - Primer Distrito|3|8|155|63|54|91|92|1
Capital - Primer Distrito|4|9,10|151|71|66|75|79|4
Capital - Primer Distrito|5|10,11|169|86|76|82|88|2
Capital - Primer Distrito|6|11|174|82|81|79|81|
Capital - Segundo Distrito|1|12,13|166|76|74|87|85|2
Capital - Segundo Distrito|2|13,15|164|48|46|106|106|
Capital - Segundo Distrito|3|14|168|70|69|100|105|
Capital - Segundo Distrito|4|14,26,27|86|38|34|48|52|
Capital - Tercer Distrito|1|16,26,27|167|74|72|79|79|23
Capital - Tercer Distrito|2|17|175|77|77|94|97|
Capital - Tercer Distrito|3|17,18|176|80|80|77|77|3
Capital - Tercer Distrito|4|18,26,27,28|224|123|124|96|99|2'''
NAMES=['Augusto Echegaray','Estanislao Albarracín','Luis R. Brandam','Pedro A. Garro']
def build():
    rows=[];controls=[];totals=collections.defaultdict(int)
    for line in RAW.splitlines():
        unit,mesa,pages,voters,*tail=line.split('|');*votes,blank=tail;votes=list(map(int,votes))
        note='Votos por candidato, transcripción visual 2026-10-15. Nombre territorial literal del colegio electoral; no homologado a departamento moderno. No se suman candidatos como listas excluyentes.'
        date='7/4/1912'
        if 'complementaria' in mesa:
            date='21/4/1912';note+=' Elección COMPLEMENTARIA del 21 de abril, escrutada el 24. No se suma al escrutinio anulado del 7/4 ni se fecha como comicio original.'
        note+=' Cobertura de los cuatro candidatos principales; los votos dispersos citados en el expediente aún no están transcritos exhaustivamente. No homologar automáticamente colegios/localidades con los colegios enumerados en el resumen provincial.'
        note+=' Revisión nominal: Pedro A. Garro, leído erróneamente Cano en la transcripción inicial. Echegaray/Etchegaray y Brandam/Brandan conservan reserva de grafía.'
        if unit=='Caucete' and mesa=='3':note+=' Reservada PDF 68 y admitida/escrutada PDF 73-74; no es complementaria.'
        if unit=='Veinticinco de Mayo' and mesa=='1':note+=' Reservada PDF 69 y admitida/escrutada PDF 73-75; no es complementaria.'
        if unit=='Albardón' and mesa=='5 y fracción':note+=' El acta reúne mesa quinta y fracción; se conserva como un registro conjunto sin desagregar.'
        if unit=='Rivadavia' and mesa=='3':note+=' PDF 35 dice veintisiete para Echegaray y veintisiete para Albarracín; lectura ampliada conservada en san_juan_rivadavia3_detalle2.png. No se cambia a 97 por simetría o cierre provincial.'
        note+=' Resumen PDF 85: la Junta declara haber eliminado al azar o considerado blancos diferencias entre sobres y actas en mesas reservadas. El detalle transcrito no queda certificado como resultado final corregido por mesa.'
        if unit=='Concepción' and mesa in ['4','6','7','8','9']:note+=' Se conserva sufragantes declarados en el acta inicial, discrepantes con sobres; escrutinio posterior PDF 26-30.'
        if unit.startswith('Capital') and (unit,mesa) in [('Capital - Segundo Distrito','4'),('Capital - Tercer Distrito','1'),('Capital - Tercer Distrito','4')]:note+=' Reservada inicialmente; cifras del escrutinio posterior PDF 26-28. Sufragantes declarados iniciales, sin reemplazar por sobres.'
        known=sum(votes)
        # Diagnóstico condicional, no imputación: cada elector podía votar dos candidatos.
        controls.append(dict(unidad_fuente=unit,mesa=mesa,paginas_pdf=pages,fecha_comicio=date,sufragantes=voters,suma_votos_candidatos=known,blancos_expresos=blank,diferencia_candidatos_menos_dos_por_sufragante=known-2*int(voters) if voters else '',diferencia_si_cada_blanco_fuera_sobre_con_dos_votos=known+2*int(blank)-2*int(voters) if blank and voters else '',nota='El segundo diagnóstico supone blanco por sobre: no prueba que todas las menciones sean equivalentes; no se rellena diferencia. '+note))
        for name,value in zip(NAMES,votes):
            totals[(unit,name)]+=value
            rows.append(dict(provincia='San Juan',unidad_fuente=unit,mesa=mesa,candidato=name,votos=value,fecha_comicio=date,paginas_pdf=pages,fuente_id='27-d-1912',nota=note))
    for file,items in [('san_juan_mesas_candidatos.csv',rows),('san_juan_mesas_controles.csv',controls)]:
        with (P/file).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
    provincial={'Augusto Echegaray':8853,'Estanislao Albarracín':8759,'Luis R. Brandam':8506,'Pedro A. Garro':8593}
    audit={'posiciones_transcritas':len(controls),'mesas_declaradas_fuente':107,'fuente_conteo':'27-D PDF 78 y 81. Albardón 5 y fracción en registro conjunto; la coincidencia del conteo no certifica identidad geográfica.', 'cotejo':[dict(candidato=n,suma_cifras_expresas=sum(v for (u,c),v in totals.items() if c==n),total_provincial_pdf82=provincial[n],diferencia=sum(v for (u,c),v in totals.items() if c==n)-provincial[n]) for n in NAMES], 'estado':'No armonizado: cobertura de cuatro candidatos; diferencias conservadas y votos dispersos pendientes. PDF 85 declara ajustes de sobres/actas en mesas reservadas sin detallar aquí su distribución por candidato.'}
    (P/'san_juan_cotejo_provincial.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([dict(unidad=u,candidato=c,votos=v) for (u,c),v in totals.items()],ensure_ascii=False,indent=2))
    return totals
if __name__=='__main__':build()
