"""Corrección de mayúsculas y espacio de las etiquetas del Sankey."""
from pathlib import Path
p=Path(__file__).resolve().parent/'visor.html'
t=p.read_text(encoding='utf8')
if "'JSRN':'JSRN'" not in t:
 t=t.replace('const labels={',"const labels={'JSRN':'JSRN','MPN':'MPN','FITU':'FIT-U','NOS':'NOS','MOVIPRO':'MOVIPRO','PROCLAME':'PROCLAME','UCR':'UCR',",1)
t=t.replace(".replace(/^FRENTE /,'Frente ')",'')
t=t.replace('gap=43,x0=230','gap=55,x0=230')
p.write_text(t,encoding='utf8')
