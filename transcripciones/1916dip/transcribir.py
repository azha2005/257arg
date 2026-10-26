import csv,json,zipfile
from pathlib import Path
from collections import Counter
BASE=Path(__file__).resolve().parent
OUT=BASE/'resultado'; OUT.mkdir(exist_ok=True)
# Lectura visual de la página 6; conservar la etapa del escrutinio original.
raw='''Rectoral (Cap.)|831|815|1112|1096|2008|Capital
Candelaria (Cap.)|735|725|963|955|1742|Capital
Caldera|216|216|119|119|342|La Caldera
Campo Santo|214|214|151|157|370|Campo Santo
Güemes|213|213|131|131|438|Campo Santo
Metán|528|381|315|170|723|Metan
Galpón|106|106|89|89|199|Metan
San José de Orquera|105|105|70|70|177|Metan
Anta|180|180|146|146|338|Anta
Chañar Muyo|342|341|118|114|464|Anta
Rivadavia|120|120|81|81|205|Rivadavia
Orán|275|275|189|189|470|Oran
San Andrés|237|237|4|4|248|Oran
Luna Muerta|44|44|70|70|116|Oran
Campo Durán|53|53|2|2|57|Oran
Iruya|469|469|160|160|644|Iruya
Santa Victoria|508|508|31|31|588|Santa Victoria
Cerrillos|342|342|215|214|563|Cerrillos
La Merced|336|265|121|50|393|Cerrillos
Chicoana|467|430|252|215|701|Chicoana
Carril|180|167|114|114|293|Chicoana
La Viña|213|213|95|95|376|La Viña
Coronel Moldes|140|111|215|186|344|La Viña
Guachipas|198|198|143|143|346|Guachipas
Carahuasi|203|203|69|69|277|Guachipas
Rosario de la Frontera|504|504|96|97|621|Rosario de la Frontera
Las Mercedes|277|277|49|49|334|Rosario de la Frontera
Candelaria (Tala)|284|284|110|110|399|La Candelaria
Cafayate|533|503|346|316|853|Cafayate
San Carlos|260|260|132|132|401|San Carlos
Angastaco|175|175|136|136|314|San Carlos
Molinos|362|362|170|170|550|Molinos
Luracatao|337|337|0|0|337|Molinos
Cachi|423|415|267|259|688|Cachi
Rosario de Lerma|316|305|307|296|625|Rosario de Lerma
Silleta|168|168|79|79|261|Rosario de Lerma
Quebrada del Toro|155|156|55|54|213|Rosario de Lerma
La Poma|208|208|1|1|211|La Poma'''
names=['Agustín Usandivaras','Julio Cornejo','Carlos Outes','Abraham Echazú']
final=[11339,10967,6723,6369]
rows=[]
for num,line in enumerate(raw.splitlines(),1):
 p=line.split('|'); vals=list(map(int,p[1:5])); dept=p[6]
 rows.append(dict(colegio_numero=num,colegio_nombre=p[0],**dict(zip(names,vals)),sufragantes=int(p[5]),notas_lectura='Outes 151/157 y Echazu 157/151: lecturas tentativas, ver lecturas_dudosas' if num==4 else ('Outes y Echazu: guiones interpretados como cero' if num==33 else ''),departamento_1914_candidato=dept,estado_enlace='pendiente de delimitacion de 1916' if dept else 'sin resolver',pagina_votos=6,pagina_sufragantes=15,fecha_acta='1916-04-15',etapa='escrutinio anterior a complementaria del 23 de abril'))
def save(name,data):
 (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 if data:
  with (OUT/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
save('colegios_diputados_15abril',rows)
save('lecturas_dudosas',[dict(colegio_numero=4,candidato='Carlos Outes',lectura_preferida=151,lectura_alternativa=157,pagina_pdf=6,estado='tentativa; extremo del trazo final ambiguo',efecto='151 permite conciliar total de columna; no prueba por si solo la lectura'),dict(colegio_numero=4,candidato='Abraham Echazú',lectura_preferida=157,lectura_alternativa=151,pagina_pdf=6,estado='tentativa; extremo del trazo final ambiguo',efecto='157 permite conciliar total de columna; no prueba por si solo la lectura')])
checks=[dict(candidato=n,suma_38_colegios=sum(r[n] for r in rows),total_escrito_p6=t,proclamacion_1mayo=f,diferencia_final_menos_suma=f-sum(r[n] for r in rows),diferencia_total_p6_menos_suma=t-sum(r[n] for r in rows),estado='lectura revisada; falta conciliar etapas y aritmetica fuente') for n,t,f in zip(names,[11257,10885,6723,6369],final)]
save('cotejo_totales',checks)
minor=[('Eliseo M. Lesser',121),('José R. Piniella',120),('Leonardo Frisia',2),('Pedro Campos Pérez',2),('Mamerto Villagrán',1),('Indalecio Gómez',2),('Manuel Anzoátegui',1),('Carlos Ibarguren',1),('Manuel R. Alvarado',1),('Alberto Alemán',1),('B. Juarez',1),('Luis Peralta',1)]
planilla_minor=['Eliseo M. Lesser','José R. Piniella','Leonardo Frisia','Pedro Campos Pérez','Luis Peralta','Mamerto Villagrán','Indalecio Gómez','Alberto Alemán','Manuel Anzoátegui','Manuel R. Alvarado','Carlos Ibarguren','B. Juarez']
positivos={1:[21,21,1,1,1,1,2,None,None,None,1,None],2:[10,9,1,1,None,None,None,1,1,1,None,None],4:[2,2],5:[82,82],6:[5,5],26:[None]*11+[1],27:[1,1]}
long=[]
for r in rows:
 for n in names:
  long.append(dict(colegio_numero=r['colegio_numero'],colegio=r['colegio_nombre'],candidato=n,votos=r[n],marca_fuente='guion' if r['colegio_numero']==33 and n in names[2:] else 'cifra',estado='lectura dudosa, ver lecturas_dudosas' if r['colegio_numero']==4 and n in names[2:] else 'lectura visual; cotejo de columna sujeto a lecturas_dudosas',fecha='1916-04-15',pagina_pdf=6))
 for i,n in enumerate(planilla_minor):
  vals=positivos.get(r['colegio_numero'],[]); v=vals[i] if i<len(vals) else None
  dash=r['colegio_numero']==1 and i in [7,8,9,11]
  long.append(dict(colegio_numero=r['colegio_numero'],colegio=r['colegio_nombre'],candidato=n,votos=0 if dash else v,marca_fuente='cifra' if v is not None else ('guion' if dash else 'celda vacia'),estado='lectura visual; vacios conservados como desconocidos' if v is None and not dash else 'lectura visual',fecha='1916-04-15',pagina_pdf=6))
save('diputados_por_colegio_todas_columnas',long)
save('cotejo_minor_planilla',[dict(candidato=n,suma_cifras_explicitas=sum(x['votos'] or 0 for x in long if x['candidato']==n),proclamacion_1mayo=dict(minor)[n],vacios_no_convertidos_a_cero=True) for n in planilla_minor])
save('diputados_proclamacion_1mayo',[dict(candidato=n,votos=v,pagina_pdf=12,fecha='1916-05-01',nivel='provincia',cargo='diputado nacional') for n,v in list(zip(names,final))+minor])
electores=[('Juan Mónico',10907),('César Cánepa Villar',10881),('Juan R. Uriburu',10909),('Ricardo E. Dávalos',10909),('Silvano Murua',10908),('Serafín Domínguez',10907),('Nemecio Costas',10907),('Silverio Chavarria',10907),('Abraham Echazú',6767),('David M. Saravia',6769),('Carlos Outes',6768),('José María Navamuel',6767),('Vicente Diez',6765),('Julio Sueldo',6765),('Jacinto F. Córdoba',6765),('Aníbal Figueroa',6767),('César Mónico',27),('Ernesto Alarcón',120),('Quintín Conde',120),('Ramón C. Díaz',120),('Julio L. González',120),('Alberto Gonzales',120),('Víctor Onesti',120),('Eliseo M. Lesser',120),('Lucio Plaza',120),('Darío Arias',1),('Santiago Gutiérrez',1),('Secundino A. Gómez',1),('Aniceto Latorre',1),('Francisco R. Sosa',1)]
save('electores_proclamacion_1mayo',[dict(candidato=n,votos=v,pagina_pdf=12 if i<21 else 13,fecha='1916-05-01',nivel='provincia',cargo='elector de presidente y vicepresidente') for i,(n,v) in enumerate(electores)])
local_inventory=BASE/'inventario_1914_salta.json'
inventory=json.loads((local_inventory if local_inventory.exists() else BASE.parent/'output/geografia_historica/inventario_unidades.json').read_text())
salta=[x for x in inventory if x['anio']==1914 and x['prov_codigo_actual']=='66']
geo=[]
for x in salta:
 terr=x['nombre'] in ['San Antonio de los Cobres','Pastos Grandes']
 candidates=[r for r in rows if r['departamento_1914_candidato']==x['nombre']]
 geo.append(dict(nombre_capa=x['nombre'],codigo_capa=x['codigo_fuente'],jurisdiccion_historica='Territorio de Los Andes' if terr else 'Salta',incluir_en_eleccion_salta_1916='no' if terr else 'si, previa verificacion de limites',colegios_candidatos='; '.join(str(r['colegio_numero'])+' '+r['colegio_nombre'] for r in candidates),fuente='Cacopardo cuadro 1 pp.35-37 (PDF40-42); capa Departamentos_1914',estado='exclusion documentada' if terr else 'enlace nominal, delimitacion electoral pendiente'))
save('cruce_cacopardo_capa1914',geo)
save('correspondencias_colegios',[dict(colegio_numero=r['colegio_numero'],colegio=r['colegio_nombre'],departamento_candidato=r['departamento_1914_candidato'],estado=r['estado_enlace'],fundamento='coincidencia nominal con Cacopardo' if r['colegio_nombre'] in ['Anta','Cachi','Cafayate','Caldera','Campo Santo','Cerrillos','Chicoana','Guachipas','Iruya','La Viña','Molinos','Orán','Rivadavia','San Carlos','Metán','Santa Victoria','La Poma','Rosario de Lerma','Rosario de la Frontera'] else 'hipotesis de agrupacion territorial; requiere padron/decreto completo') for r in rows])
save('incidencias',[dict(colegio=11,unidad='Rivadavia',mesa='5',paginas_pdf='5; 15; 49-50; 54; 11',incidencia='Anulacion y eleccion complementaria el 23 de abril; el acta del 15 de abril es anterior.',tratamiento='No sustituir el total de Rivadavia con la diferencia provincial sin resolver otras correcciones.'),dict(colegio=5,unidad='Güemes',mesa='5',paginas_pdf='40; 52',incidencia='Decision inicial y reconsideracion de votos.',tratamiento='Reconstruir secuencia antes de aplicar ajustes.'),dict(colegio=22,unidad='La Viña',mesa='2',paginas_pdf='38',incidencia='Diez votos de Union Provincial previamente excluidos.',tratamiento='Verificar si ya incorporados en planilla del 15 de abril.'),dict(colegio=23,unidad='Coronel Moldes',mesa='1',paginas_pdf='38',incidencia='Trece votos de Union Provincial previamente excluidos.',tratamiento='Verificar si ya incorporados en planilla del 15 de abril.')])
print(json.dumps(checks,ensure_ascii=False));print('Sufragantes',sum(r['sufragantes'] for r in rows));print('Poligonos',len(geo),'; Salta historica',sum(x['jurisdiccion_historica']=='Salta' for x in geo))
