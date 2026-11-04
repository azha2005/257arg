"""Índice local autocontenido, filtrable; no requiere conexión ni altera geometría."""
from pathlib import Path
import json,html,collections
ROOT=Path(__file__).resolve().parent.parent/'catalogo_shp'
rows=json.loads((ROOT/'catalogo.json').read_text(encoding='utf-8'))
data=[]
for r in rows:
    m=r['metadata_original']
    data.append(dict(anio=r['anio_carpeta'],tipo=r['tipo'],archivo=r['shp'],origen=m['archivo'],n=r['entidades'],carpeta=r['carpeta'],nota=r['criterio_anio'],faltan=', '.join(r['faltan_componentes'])))
payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
page='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Cartografía argentina · SHP</title>
<style>body{font:16px system-ui;margin:30px;color:#203043}h1{font-size:26px}input,select{font:inherit;padding:8px;margin:0 8px 10px 0}input{width:380px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:9px;border-bottom:1px solid #d6dee5}th{background:#e9f0f5;position:sticky;top:0}a{color:#145b9b}small{display:block;color:#526174}#n{margin:10px 0}tr:hover{background:#f4f8fb}</style>
<h1>Cartografía argentina: shapefiles por año</h1><p>Una carpeta por capa, con componentes originales y procedencia. Los años de copia no certifican vigencia. Las capas auxiliares y las copias de distintas fuentes se conservan identificadas.</p>
<p><a href="../circuitos_serie/INDICE.html">Serie nacional de circuitos 2003–2026</a> · <a href="LEEME.md">Informe del catálogo</a> · <a href="../cartografia_argentina/LEEME.md">Fuentes, cobertura y limitaciones</a> · <a href="catalogo.json">Metadatos completos</a></p>
<input id="q" placeholder="Buscar localidad, provincia, fuente o archivo…" aria-label="Buscar"><select id="year" aria-label="Año"><option value="">Todos los años</option></select><select id="type" aria-label="Tipo"><option value="">Todos los tipos</option></select><div id="n"></div>
<table><thead><tr><th>Año</th><th>Tipo</th><th>Capa y procedencia</th><th>Entidades</th><th>Archivos</th></tr></thead><tbody id="body"></tbody></table>
<script>const rows=PAYLOAD;const $=id=>document.getElementById(id);for(const [id,key]of[['year','anio'],['type','tipo']])for(const v of [...new Set(rows.map(r=>r[key]))].sort()){const o=document.createElement('option');o.value=v;o.textContent=v;$(id).append(o)}
function cell(tr,s){const td=document.createElement('td');td.textContent=s;tr.append(td);return td}function link(td,label,path){const a=document.createElement('a');a.textContent=label;a.href=path.split('/').map(encodeURIComponent).join('/');td.append(a)}
function render(){const q=$('q').value.toLocaleLowerCase('es');const filtered=rows.filter(r=>(!$('year').value||r.anio===$('year').value)&&(!$('type').value||r.tipo===$('type').value)&&(!q||[r.origen,r.archivo,r.tipo,r.anio].join(' ').toLocaleLowerCase('es').includes(q)));$('n').textContent=filtered.length+' capas de '+rows.length+'. Las repeticiones de procedencia no equivalen a delimitaciones independientes.';$('body').replaceChildren();const frag=document.createDocumentFragment();for(const r of filtered){const tr=document.createElement('tr');cell(tr,r.anio).title=r.nota;cell(tr,r.tipo);const title=cell(tr,r.archivo);const sm=document.createElement('small');sm.textContent=r.origen;title.append(sm);cell(tr,r.n.toLocaleString('es-AR'));const files=cell(tr,'');link(files,'SHP',r.carpeta+'/'+r.archivo);files.append(' · ');link(files,'Fuente y componentes',r.carpeta+'/LEEME.md');if(r.faltan){const s=document.createElement('small');s.textContent='Falta '+r.faltan;files.append(s)}frag.append(tr)}$('body').append(frag)}for(const id of ['q','year','type'])$(id).addEventListener('input',render);render();</script></html>'''
(ROOT/'CATALOGO.html').write_text(page.replace('PAYLOAD',payload),encoding='utf-8')
readme=ROOT/'LEEME.md';text=readme.read_text(encoding='utf-8')
if '../circuitos_serie/INDICE.html' not in text:
    text=text.replace('# Shapefiles por año y capa\n','# Shapefiles por año y capa\n\nAdemás de los originales de este catálogo, está la [serie nacional de circuitos 2003–2026](../circuitos_serie/INDICE.html), con versiones documentadas y aproximadas separadas.\n',1)
    readme.write_text(text,encoding='utf-8')
# Inventarios anuales cortos para navegar sin el visor HTML.
from urllib.parse import quote
for year in sorted(set(r['anio_carpeta'] for r in rows)):
    lines=['# Shapefiles '+year,'','Cada enlace abre las notas de una carpeta con un único SHP.','', '| Tipo | Archivo original | Capa | Entidades |','|---|---|---|---:|']
    for r in rows:
        if r['anio_carpeta']!=year:continue
        relative='/'.join(r['carpeta'].split('/')[1:])+'/LEEME.md'
        lines.append(f'| {r["tipo"]} | {r["metadata_original"]["archivo"]} | [{r["shp"]}]({quote(relative)}) | {r["entidades"]} |')
    (ROOT/year/'INVENTARIO.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Índice HTML y',len(set(r['anio_carpeta'] for r in rows)),'inventarios anuales')
