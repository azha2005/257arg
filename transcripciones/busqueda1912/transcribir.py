"""Transcripción visual; no se usa OCR para poblar votos. Ejecutar desde cualquier carpeta."""
from pathlib import Path
import csv, json, collections, contextlib, io
P=Path(__file__).resolve().parent
# Nombre; inscriptos; votantes; columnas políticas, en el orden de la clave impresa.
CAP='''Balvanera Norte;3875;3346;1172;1112;1425;1056;664
Balvanera Oeste;6872;5774;2185;1920;1787;1663;1065
Balvanera Sud;3681;3125;1117;1075;1092;971;574
Belgrano;5432;4680;1681;1337;1553;1440;764
Concepción;6427;5628;2463;1688;1906;1505;758
Flores;5594;4859;1517;1141;1462;1718;580
Las Heras;8882;7497;2656;2410;2355;2254;1543
Monserrat;7273;5965;2283;1849;2648;2044;1052
Palermo;5359;4264;1478;1187;1322;1186;696
Pilar;8915;7662;2609;2832;3346;2473;1662
San Bernardo;4136;3309;982;758;701;1009;852
San Carlos Norte;5469;4768;1346;884;1340;975;348
San Carlos Sud;5536;4877;1699;1747;1439;1407;931
San Cristóbal Norte;7021;6028;2155;2051;1589;1666;917
San Cristóbal Sud;4684;3931;1264;1159;719;1037;574
San Juan Evangelista;9380;7070;1990;2605;935;1041;671
San Nicolás;6256;5186;1768;1515;2330;1858;1047
Santa Lucía;9124;7941;2888;2994;1745;1599;897
Socorro;4527;3896;1442;1140;1918;1372;776
Vélez Sarsfield;5493;4644;1201;1047;1127;1600;725'''
COR='''Calamuchita;2312;2032;99;333;858;742
Capital;20453;13564;5820;1985;2928;2831
Colón;2968;1916;327;610;593;386
Cruz del Eje;5153;3498;615;769;1335;779
General San Martín;6189;3533;1089;406;1158;880
Ischilín;2540;1827;405;595;500;327
Minas;1136;616;1;110;476;29
Pocho;994;792;3;220;429;140
Río Cuarto;9569;2822;182;1216;1089;335
Río Primero;5931;2665;394;1513;751;7
Río Seco;1269;644;134;97;183;230
Río Segundo;5561;2877;1032;197;969;679
San Alberto;2613;2036;269;257;1235;275
San Javier;2938;1846;184;680;978;4
San Justo;8461;3963;1746;1015;688;514
Santa María;3013;2972;304;1077;1239;352
Sobremonte;1000;434;21;169;241;3
Tercero Arriba;3617;2721;472;193;941;1115
Totoral;2013;1483;13;359;787;324
Tulumba;2810;1276;126;523;586;41
Unión;5949;3631;775;505;1468;883'''
FIELDS=['provincia','departamento','partido_o_lista','votos','fila_fuente','fuente_id','nota']
def write(name,rows,fields):
    with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def run():
    rows=[];controls=[];totals=collections.defaultdict(int)
    for prov,table,parties,page in [('Capital Federal',CAP,['Unión Cívica Radical','Socialista [columna 4]','Unión Cívica','Unión Nacional','Unión Comunal'],17),('Córdoba',COR,['Unión Cívica Radical','Unión Nacional','Constitucional','Autonomista Nacional'],18)]:
        for line in table.splitlines():
            dep,*nums=line.split(';'); ins,vot,*votes=map(int,nums)
            note='Transcripción manual de imagen; consulta 2026-10-15; denominaciones de Cantón; no convertidos a votos individuales de electores.'
            if prov=='Capital Federal':note+=' Título 1912 pero fuente impresa La Nación 7 y 14/4/1916; fecha pendiente de cotejo. Columna 4 sin clave tipográfica visible, identificada por anotación manuscrita Socialista; conservar reserva.'
            for party,value in zip(parties,votes):
                rows.append(dict(zip(FIELDS,[prov,dep,party,value,f'Tomo II PDF {page}, p. impresa {page-14}, fila {dep}','canton-II-1912',note])))
                totals[(prov,party)]+=value
            controls.append(dict(provincia=prov,departamento=dep,inscriptos=ins,votantes=vot,suma_columnas=sum(votes),diferencia_suma_menos_votantes=sum(votes)-vot,nota='Capital: la fuente advierte que las sumas exceden votantes/inscriptos; no son listas excluyentes.' if prov=='Capital Federal' else ('Cierra.' if sum(votes)==vot else 'No cierra; conservar sin ajustar.')))
        missing={'Puerto':'Unidad censal; no se aplica a la división electoral (tomo I, XLVII/PDF 50).'} if prov=='Capital Federal' else {'General Roca':'Incluido en Juárez Celman (tomo I, XLVIII/PDF 51), también sin cifras en 1912.','Juárez Celman':'** en tabla 1912; el apéndice no identifica una unidad receptora.','Marcos Juárez':'** en tabla 1912; el apéndice no identifica una unidad receptora.','Presidente Roque Sáenz Peña':'Incluido en Juárez Celman (tomo I, XLVIII/PDF 51), también sin cifras en 1912.','Punilla':'** en tabla 1912; el apéndice no identifica una unidad receptora.'}
        for dep,note in missing.items():
            for party in parties:rows.append(dict(zip(FIELDS,[prov,dep,party,'',f'Tomo II PDF {page}, fila {dep}','canton-II-1912','** original; no es cero. '+note])))
    # Diario Santa Fe, 23/4/1912, p. 1, columna «La Junta Escrutadora Nacional».
    sf={
        'Vera':[('Miguel Coronado',1824),('Francisco G. Valdez',1825),('Benjamín Ábalos',1824),('Rogelio Araya',1825),('Gregorio García Vieyra',1058),('Víctor P. Pesenti',1059),('Domingo Regules',1058),('Hernán Saavedra Lamas',1058),('Néstor N. Fernández',396),('Julián Paz',121),('Laureano Araya',506),('Antonio Cafferata',1),('C. Pera',1)],
        'Belgrano':[('Miguel Coronado',183),('Francisco G. Valdez',183),('Francisco G. Valdez',933),('Benjamín Ábalos',183),('Rogelio Araya',183),('Lisandro de la Torre',666),('Cornelio Casablanca',666),('Gregorio García Vieyra',662),('Víctor P. Pesenti',662),('Domingo Regules',661),('Hernán Saavedra Lamas',661),('Néstor N. Fernández',2),('Juan Carlos Crouzeilles',1)]}
    sf['Rosario']=[('Rogelio Araya',9614),('Miguel Coronado',''),('Benjamín Ábalos',9506),('Francisco G. Valdez',9489),('Lisandro de la Torre',6077),('Cornelio Casablanca',5706),('Fermín Lejarza',5435),('Ovidio A. Lagos',5329),('Víctor P. Pesenti',1747),('Domingo Regules',1591),('Néstor N. Fernández',1530),('Gregorio García Vieyra',1459),('Hernán Saavedra Lamas',1376)]
    sf['Las Colonias']=[('Miguel Coronado',2702),('Francisco G. Valdez',2699),('Benjamín Ábalos',2699),('Rogelio Araya',2701),('Gregorio García Vieyra',1740),('Víctor P. Pesenti',1271),('Domingo Regules',1271),('Hernán Saavedra Lamas',1470),('Juan Carlos Crouzeilles',9),('Julián Paz',6),('Néstor de Iriondo',6),('Laureano Araya',6),('Lisandro de la Torre',6),('Antonio Cafferata',6),('Estanislao M. López',3),('Rodolfo B. Lehmann',1),('Ignacio Iturraspe',1),('Marcial R. Candioti',1)]
    sf['San Lorenzo']=[('Miguel Coronado',1324),('Francisco G. Valdez',1310),('Benjamín Ábalos',1314),('Rogelio Araya',1313),('Gregorio García Vieyra',130),('Víctor P. Pesenti',26),('Domingo Regules',128),('Hernán Saavedra Lamas',23),('Néstor N. Fernández',28),('Lisandro de la Torre',1440),('Cornelio Casablanca',''),('Ovidio A. Lagos',1429),('Fermín Lejarza',1434),('Antonio Cafferata',105),('Marcial R. Candioti',2),('Juan Arzeno',1),('Richeri',1),('Lazo',1)]
    for dep,entries in sf.items():
        idx,date=(6509,'18/4/1912') if dep=='Rosario' else ((6510,'20/4/1912') if dep in ['Las Colonias','San Lorenzo'] else (6512,'23/4/1912'))
        for i,(candidate,value) in enumerate(entries,1):
            note='Votos por candidato; transcripción manual de imagen, 2026-10-15. Escrutinio parcial: el artículo informa 17 mesas complementarias aún pendientes; no se suman candidatos como si fueran votantes o listas excluyentes.'
            if dep=='Belgrano' and candidate=='Francisco G. Valdez':note+=' El impreso repite el mismo nombre con 183 y 933; se conservan ambas líneas sin decidir cuál es correcta ni sumarlas entre sí.'
            if value=='':note+=' Cifra visible pero lectura no segura; pendiente de cotejo; no se usa un valor aproximado.'
            rows.append(dict(zip(FIELDS,['Santa Fe',dep,'Candidato: '+candidate,value,f'Diario Santa Fe {date}, p. 1, {dep}, línea {i}',f'santa-fe-{idx}',note])))
    # Las ampliaciones se reproducen desde sus transcripciones de imágenes.
    from mendoza_departamentos import build as build_mendoza
    from san_juan_parcial import build as build_sanjuan
    with contextlib.redirect_stdout(io.StringIO()):
        mt=build_mendoza(); build_sanjuan()
    mrows=list(csv.DictReader((P/'mendoza_mesas_candidatos.csv').open(encoding='utf-8-sig')))
    mg=collections.defaultdict(list)
    for r in mrows:mg[(r['unidad_fuente'],r['candidato'])].append(r)
    for (unit,candidate),items in mg.items():
        note='Suma de cifras expresas por mesa; fuente primaria 42-D, consulta 2026-10-15. No se suman original anulado y complementaria. Ciudad de Mendoza conserva la unidad literal, sin homologación geométrica. Menores: suma recuperada 70 frente a 74 provinciales; diferencia -4 sin imputar. Véase mendoza_cotejo_provincial.json para errores internos.'
        status=next((t for t in mt if t['unidad_fuente']==unit and t['candidato']==candidate),None)
        if status and not status['completo_candidato']:note+=f" SUMA PARCIAL DE CIFRAS EXPRESAS: faltan valores en mesa(s) {status['mesas_sin_cifra']}; no se convierten en cero aunque los totales provinciales principales cierren."
        if candidate not in ['Pedro Benegas','Estanislao D. Gaviola']:note+=' Candidato disperso; no se certifica exhaustividad de votos menores por unidad.'
        pages=sorted({int(p) for r in items for p in r['paginas_pdf'].split(',')})
        rows.append(dict(zip(FIELDS,['Mendoza',unit,'Candidato: '+candidate,sum(int(r['votos']) for r in items),'42-D-1912 PDF '+','.join(map(str,pages))+'; mesas en mendoza_mesas_candidatos.csv','42-d-1912',note])))
    sj=list(csv.DictReader((P/'san_juan_mesas_candidatos.csv').open(encoding='utf-8-sig')))
    groups=collections.defaultdict(list)
    for r in sj:groups[(r['unidad_fuente'],r['candidato'])].append(r)
    for (unit,candidate),items in groups.items():
        pages=sorted({int(p) for r in items for p in r['paginas_pdf'].split(',')})
        rows.append(dict(zip(FIELDS,['San Juan',unit,'Candidato: '+candidate,sum(int(r['votos']) for r in items),'27-D-1912 PDF '+','.join(map(str,pages))+'; mesas en san_juan_mesas_candidatos.csv','27-d-1912',items[0]['nota']+' Hay diferencias entre candidatos/blancos/sufragantes: ver controles, no se imputa.'])))
    write('datos_1912_depto.csv',rows,FIELDS)
    write('controles_canton.csv',controls,list(controls[0]))
    write('sumas_canton.csv',[dict(provincia=p,partido_o_lista=g,suma=s) for (p,g),s in totals.items()],['provincia','partido_o_lista','suma'])
    print(json.dumps(dict(filas=len(rows),numericas=sum(r['votos']!='' for r in rows),vacias=sum(r['votos']=='' for r in rows),cordoba_no_cierran=[r for r in controls if r['provincia']=='Córdoba' and r['diferencia_suma_menos_votantes']]),ensure_ascii=False,indent=2))
if __name__=='__main__':run()
