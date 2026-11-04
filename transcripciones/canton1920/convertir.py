import json,re,pathlib
root=pathlib.Path('transcripciones/canton1920')
keys={56:['Inscriptos','Votantes','Unión Cívica Radical','Socialista','Demócrata','Socialista Argentino'],57:['Inscriptos','Votantes','Unión Cívica Radical','Conservadores','Socialista'],61:['Inscriptos','Votantes','Unión Cívica Radical','Socialista','Demócrata'],62:['Inscriptos','Votantes','Unión Cívica Radical','Liberal'],63:['Inscriptos','Votantes','Unión Cívica Radical','Socialista','En blanco'],64:['Inscriptos','Votantes','Socialista','Demócrata','Liberal'],65:['Inscriptos','Votantes','Socialista','Unión Cívica Radical Lencinista','Autonomista','Radical Situacionista'],66:['Inscriptos','Votantes','Unión Cívica Radical','Demócrata','Unión Popular'],67:['Inscriptos','Votantes','Unión Cívica Radical','Demócrata Progresista'],68:['Inscriptos','Votantes','Unión Cívica Radical','Liberal']}
for n in (58,59,60): keys[n]=keys[57]
pages={}
for line in (root/'manual1920.txt').read_text(encoding='utf-8-sig').splitlines():
 if line.startswith('# PDF '):
  m=re.match(r'# PDF (\d+) \| (.*?) \| libro (\d+)',line); n=int(m[1]); cols=keys[n]
  pages[n]={'anio':1920,'tomo':'II','pagina_pdf':n,'pagina_libro':int(m[3]),'provincia':m[2],'eleccion':'Elecciones Nacionales de Diputados','categoria':'varones solamente','columnas':{str(i+1):v for i,v in enumerate(cols)},'filas':[]}
  if n in (57,58,59,60): pages[n]['marcas_columnas']={'1':'*'}
  if n in range(62,69): pages[n]['marcas_columnas']={'1':'*','2':'*'}
  if 'marcas_columnas' in pages[n]: pages[n]['nota']='* en encabezado: sin datos en toda la columna; se reproduce por celda para preservar su ausencia.'
 elif line.strip():
  name,circ,raw=line.split('|'); vals=raw.split(); assert len(vals)==len(keys[n]),(n,name,vals)
  values={str(i+1):(int(v) if v.isdecimal() else None) for i,v in enumerate(vals)}
  marks={str(i+1):v for i,v in enumerate(vals) if not v.isdecimal()}
  pages[n]['filas'].append({'unidad':name,'circunscripcion':int(circ) if circ else None,'valores':values,'marcas':marks,'metodo':'Transcripción visual del escaneo'})
obj={'metadatos':{'obra':'Darío Cantón, Materiales para el estudio de la sociología política en la Argentina (1968), tomo II','fuente':'raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf','sha256':'fa7f66de072ce83b5f093549101a941cd492fbf2836a17c2d52c75ee324a01e6','revision':'Transcripción visual; requiere revisión independiente. Sin imputaciones. * en encabezado replicado para indicar ausencia por columna.'},'paginas':[pages[n] for n in sorted(pages)]}
(root/'canton_1920.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(pages),sum(len(p['filas']) for p in pages.values()),[(n,len(pages[n]['filas'])) for n in sorted(pages)])
