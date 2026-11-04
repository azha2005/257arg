"""Prioriza el empalme con mayor detalle sin quitar las versiones anteriores."""
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'visor.html'
t=P.read_text(encoding='utf8')
old="options('pair',list.map(d=>[d.id,d.origen+' → '+d.destino]),id);loadPair()"
new="let preferred=id||[...list].sort((a,b)=>b.unidades-a.unidades)[0]?.id;options('pair',list.map(d=>[d.id,d.origen+' → '+d.destino]),preferred);loadPair()"
if old in t:t=t.replace(old,new)
P.write_text(t,encoding='utf8')
