from pathlib import Path
import csv,hashlib,json
P=Path(__file__).resolve().parent;F=P/'fuentes'
rows=[r for r in csv.DictReader((P/'fuentes.csv').open(encoding='utf-8-sig')) if r['fuente_id'].endswith('-1912') and r['fuente_id']!='canton-II-1912']
for r in rows:
    r['estado']='copia local de Descargas, recuperada y abierta 2026-10-15; URL no revalidada' if r['fuente_id'] in ['19-d-1912','27-d-1912','42-d-1912'] else 'descargado de APyM y abierto 2026-10-15'
    r['sha256']=hashlib.sha256((F/r['archivo']).read_bytes()).hexdigest()
more=[
('canton-II-1912','Capital Federal; Córdoba','https://archive.org/details/1968-materiales-para-el-estudio-de-la-sociologia-2','capital_cordoba_canton_tomoII.pdf','copia local; revisión visual PDF 17-18'),
('canton-I-apendice','Capital Federal; Córdoba','https://archive.org/details/1968-materiales-para-el-estudio-de-la-sociologia-1','capital_cordoba_canton_tomoI.pdf','copia local; revisión visual PDF 50-51'),
('salta-unsa','Salta','https://portalderevistas.unsa.edu.ar/index.php/cdh/article/download/611/591/2018','salta_unsa.pdf','descargado; búsqueda en texto; fuente primaria citada, no recuperada'),
('etcheverria-diplomas','Jujuy; La Rioja; San Luis','https://cdsa.aacademica.org/000-008/2.pdf','perez_diplomas.pdf','descargado; autor Rubén Osvaldo Etcheverría; localizadores de DSCD, sin tabla departamental integrada'),
('catamarca-ibanez','Catamarca','https://cdsa.aacademica.org/000-008/124.pdf','catamarca_ibanez_alvero.pdf','copia local; descarte departamental según revisión previa del inventario'),
('mendoza-bragoni','Mendoza','https://bibliotecavirtual.unl.edu.ar/publicaciones/index.php/EstudiosSociales/article/download/2709/3886','mendoza_bragoni_mellado.pdf','copia local; cuadro departamental 1913/16/18, no 1912'),
('salta-correa','Salta','https://bibliotecavirtual.unl.edu.ar/publicaciones/index.php/EstudiosSociales/article/download/2710/3889/6681','salta_correa_quintana.pdf','copia local; cifras de Capital pendientes de cotejo primario'),
('santiago-guzman','Santiago del Estero','https://cdsa.aacademica.org/000-010/663.pdf','santiago_socialismo.pdf','copia local; 34 votos, cargo/unidad insuficientes para integrar'),
('dscd1912-indice','Mendoza; Jujuy; La Rioja','https://books.google.com/books?jscmd=SearchWithinVolume2&q=Mendoza+elecciones&vid=VrxHAQAAMAAJ','dscd_1912_0.json','respuesta pública de búsqueda interna; localizadores, NO imagen de páginas ni fuente para cifras; consultas adicionales en dscd_consultas.csv'),
]
for sid,prov,url,file,status in more:
    p=F/file
    rows.append(dict(fuente_id=sid,provincia=prov,url=url,fecha_consulta='2026-10-15',archivo=file,tamano=p.stat().st_size,estado=status,paginas='',error='',sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for idx,date in [(6504,'10/4'),(6505,'11/4'),(6506,'12/4'),(6507,'13/4'),(6508,'16/4'),(6509,'18/4'),(6510,'20/4'),(6511,'21/4'),(6512,'23/4'),(6513,'24/4'),(6514,'25/4'),(6515,'27/4'),(6516,'28/4'),(6517,'4/5')]:
    p=F/f'santa_fe_{idx}_p1_z2.png'
    if not p.exists():p=F/f'santa_fe_{idx}_p1_z2_0-4_0-4.png'
    rows.append(dict(fuente_id=f'santa-fe-{idx}',provincia='Santa Fe',url=f'https://www.santafe.gov.ar/hemeroteca/diario/{idx}/?page=1',fecha_consulta='2026-10-15',archivo=p.name,tamano=p.stat().st_size,estado=f'imagen pública por teselas; edición {date}/1912; detalles en diarios_descargas.csv',paginas=1,error='',sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
fields=list(rows[0])
with (P/'fuentes.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
controls=list(csv.DictReader((P/'controles_canton.csv').open(encoding='utf-8-sig')))
print('Controles provinciales:',{prov:{k:sum(int(r[k]) for r in controls if r['provincia']==prov) for k in ['inscriptos','votantes','suma_columnas']} for prov in ['Capital Federal','Córdoba']})
print('Fuentes registradas',len(rows))
# Tabla provincial de Wikipedia local: no son equivalentes automáticamente a sumas departamentales.
wiki={('Capital Federal','Unión Cívica Radical'):35721,('Capital Federal','Socialista [columna 4]'):32512,('Capital Federal','Unión Cívica'):32749,('Capital Federal','Unión Nacional'):29825,('Capital Federal','Unión Comunal'):17102,('Córdoba','Unión Cívica Radical'):15690,('Córdoba','Unión Nacional'):14850,('Córdoba','Constitucional'):23582}
compare=[]
for r in csv.DictReader((P/'sumas_canton.csv').open(encoding='utf-8-sig')):
    v=wiki.get((r['provincia'],r['partido_o_lista']))
    compare.append(dict(**r,wikipedia=v if v is not None else '',diferencia=int(r['suma'])-v if v is not None else '',nota='Suma de columnas de Cantón vs candidato más votado de la tabla provincial Wikipedia; cobertura/criterio no armonizados.'))
with (P/'comparacion_wikipedia.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(compare[0]));w.writeheader();w.writerows(compare)
data=list(csv.DictReader((P/'datos_1912_depto.csv').open(encoding='utf-8-sig')))
assert len(data)>=284 and sum(r['votos']=='' for r in data)==27
assert all(r['votos']=='' or int(r['votos'])>=0 for r in data)
assert all(r['fuente_id'] in {s['fuente_id'] for s in rows} for r in data)
assert all(r['diferencia_suma_menos_votantes']=='0' for r in controls if r['provincia']=='Córdoba')
print(f"CSV verificado: {len(data)} filas, {sum(r['votos']!='' for r in data)} numéricas, 27 vacías; referencias presentes.")
