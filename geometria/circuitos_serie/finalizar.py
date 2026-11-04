"""Valida salidas, empaqueta cada SHP e indexa las versiones anuales."""
from pathlib import Path
from urllib.parse import quote
import sys,json,hashlib,zipfile,collections,html,re
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'circuitos_busqueda/_deps'))
import shapefile
sources={r['id']:r for r in json.loads((ROOT/'fuentes_integrables.json').read_text(encoding='utf-8'))}
summaries=json.loads((ROOT/'resumen_anual.json').read_text(encoding='utf-8'))
errors=[];packages=[];table=[];checks=[]
for note in summaries:
    y=note['anio'];mode=note['version'];folder=ROOT/'por_anio'/str(y)/mode;path=folder/'circuitos_argentina.geojson'
    blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=note['sha256_geojson']:errors.append([y,mode,'Hash GeoJSON incorrecto'])
    j=json.loads(blob);fs=j['features'];districts=set();selected=set();bad=0;future=0
    if len(fs)!=note['entidades_geojson']:errors.append([y,mode,'Conteo GeoJSON diferente'])
    for f in fs:
        p=f['properties'];sid=p['id_fuente'];selected.add(sid);s=sources[sid];districts.add(p['codigo_distrito'])
        if p['anio_objetivo']!=y or p['version']!=mode:errors.append([y,mode,'Atribución de versión incorrecta'])
        if s.get('excluir_seleccion_automatica'):errors.append([y,mode,'Fuente aislada integrada',sid])
        if mode=='documentada' and (not s['documentada'] or not s['desde']<=y<=s['hasta']):errors.append([y,mode,'Extrapolación en documentada',sid])
        if p['anio_fuente_desde']>y:future+=1
        if not p['geometria_valida']:bad+=1
    if mode=='aproximada' and districts!={f'{i:02}' for i in range(1,25)}:errors.append([y,mode,'Falta distrito en aproximada'])
    r=shapefile.Reader(str(folder/'shp/circuitos_argentina.shp'),encoding='utf-8')
    if len(r)!=note['registros_shp']:errors.append([y,mode,'Conteo SHP diferente'])
    if r.shapeType!=5:errors.append([y,mode,'SHP no poligonal'])
    count=len(r);r.close()
    for ext in ['.shp','.shx','.dbf','.prj','.cpg']:
        if not (folder/'shp'/('circuitos_argentina'+ext)).exists():errors.append([y,mode,'Falta '+ext])
    (folder/'FUENTES.json').write_text(json.dumps([sources[s] for s in sorted(selected)],ensure_ascii=False,indent=2),encoding='utf-8')
    zip_path=folder/f'circuitos_argentina_{y}_{mode}.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for p in sorted((folder/'shp').glob('circuitos_argentina.*')):z.write(p,p.name)
        for name in ['NOTAS.json','LEEME.md','FUENTES.json']:z.write(folder/name,name)
    with zipfile.ZipFile(zip_path) as z:
        bad_member=z.testzip()
        if bad_member:errors.append([y,mode,'CRC ZIP incorrecto',bad_member])
    packages.append(dict(anio=y,version=mode,archivo=zip_path.relative_to(ROOT).as_posix(),bytes=zip_path.stat().st_size,sha256=hashlib.sha256(zip_path.read_bytes()).hexdigest()))
    check=dict(anio=y,version=mode,entidades=len(fs),registros_shp=count,distritos=len(districts),fuentes_posteriores=future,geometrias_invalidas=bad,fuentes=sorted(selected),geojson=path.relative_to(ROOT).as_posix(),zip=zip_path.relative_to(ROOT).as_posix())
    table.append(check);checks.append({k:v for k,v in check.items() if k not in ['geojson','zip']})
    print(y,mode,len(fs),count,'verificado',flush=True)
result=dict(versiones=len(table),aproximadas_con_24_distritos=sum(r['version']=='aproximada' and r['distritos']==24 for r in table),fuentes_registradas=len(sources),errores=errors,controles=checks)
(ROOT/'VALIDACION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'PAQUETES.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2),encoding='utf-8')
intro='Una composición por año, con versión documentada y aproximada separadas. Documentada no equivale a oficial: puede estar parcial o vacía. La aproximada usa fuentes anteriores o posteriores con notas por entidad. No se deducen fechas de reformas de los saltos entre archivos.'
lines=['# Índice de la serie nacional 2003–2026','',intro,'','[Metodología y alertas](LEEME.md) · [Validación](VALIDACION.json)','','| Año | Versión | Entidades | Distritos con geometría | Entidades de fuente posterior | Archivos |','|---|---|---:|---:|---:|---|']
for row in table:
    files=f'[GeoJSON]({quote(row["geojson"])}) · [SHP ZIP]({quote(row["zip"])})' if row['entidades'] else 'Pendiente: sin geometría documentada'
    lines.append(f'| {row["anio"]} | {row["version"]} | {row["entidades"]} | {row["distritos"]} | {row["fuentes_posteriores"]} | {files} |')
(ROOT/'INDICE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
body=[]
for row in table:
    if row['entidades']:
        links=f'<a href="{quote(row["geojson"])}">GeoJSON</a> · <a href="{quote(row["zip"])}">SHP ZIP</a> · <a href="por_anio/{row["anio"]}/{row["version"]}/LEEME.md">Notas</a>'
    else:links='Pendiente: sin geometría documentada'
    body.append(f'<tr data-year="{row["anio"]}" data-mode="{row["version"]}"><td>{row["anio"]}</td><td>{row["version"]}</td><td>{row["entidades"]}</td><td>{row["distritos"]}</td><td>{row["fuentes_posteriores"]}</td><td>{row["geometrias_invalidas"]}</td><td>{links}</td></tr>')
page='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Circuitos argentinos · Serie nacional</title><style>body{font:16px system-ui;max-width:1300px;margin:32px auto;padding:0 20px;color:#243447}h1{font-size:28px}.note{background:#fff3d7;padding:16px;line-height:1.5}select{font:inherit;padding:8px;margin:15px 12px 15px 0}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:10px;border-bottom:1px solid #d1dae2}th{background:#eaf0f5;position:sticky;top:0}a{color:#145b9b}tr:hover{background:#f4f8fb}</style><h1>Circuitos electorales · Argentina 2003–2026</h1><p class="note">INTRO</p><p>GeoJSON con atributos y notas completos; ZIP con SHP, SHX, DBF, PRJ, CPG y documentación. Un circuito puede tener varias entidades geométricas. Los 24 distritos presentes no garantizan cobertura territorial completa. Las geometrías inválidas se conservan identificadas (salvo componentes degenerados que GDAL no lee, retirados y anotados); el SHP extrae solo polígonos de colecciones mixtas.</p><p><a href="LEEME.md">Metodología, fuentes y alertas de georreferenciación</a> · <a href="VALIDACION.json">Validación</a> · <a href="cambios/comparacion_2021_2025.json">Comparación 2021–2025</a> · <a href="../catalogo_shp/CATALOGO.html">Catálogo de originales SHP</a></p><label>Año <select id="year"><option value="">Todos</option>YEARS</select></label><label>Versión <select id="mode"><option value="">Ambas</option><option>documentada</option><option>aproximada</option></select></label><table><thead><tr><th>Año</th><th>Versión</th><th>Entidades</th><th>Distritos</th><th>Fuente posterior al año</th><th>Geometrías inválidas</th><th>Archivos</th></tr></thead><tbody>ROWS</tbody></table><script>const year=document.getElementById('year'),mode=document.getElementById('mode');function filter(){for(const r of document.querySelectorAll('tbody tr'))r.hidden=(year.value&&r.dataset.year!==year.value)||(mode.value&&r.dataset.mode!==mode.value)}year.onchange=filter;mode.onchange=filter;</script></html>'''
page=page.replace('INTRO',html.escape(intro)).replace('YEARS',''.join(f'<option>{y}</option>' for y in range(2003,2027))).replace('ROWS',''.join(body))
(ROOT/'INDICE.html').write_text(page,encoding='utf-8')
missing=[]
for target in re.findall(r'href="([^"]+)"',page):
    if not (ROOT/target).exists():missing.append(target)
if missing:errors.extend(['Enlace local inexistente',p] for p in missing)
print('VERSIONES',len(table),'ERRORES',errors,flush=True)
if errors:raise SystemExit(1)
