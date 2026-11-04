"""Migra la primera composición al sistema del Streamlit del usuario."""
from pathlib import Path
import json
import re
HERE=Path(__file__).resolve().parent
path=HERE/'visor.html'
t=path.read_text(encoding='utf8')
if '__ESTILO__' not in t:
 t=re.sub(r'<style>.*?</style>','<style>\n__ESTILO__\n</style>',t,count=1,flags=re.S)
 t=t.replace('<title>Electorados provinciales · Sankey</title>','<title>Electorados provinciales | Sankeydron</title><meta name="description" content="Sankeys de elecciones provinciales y nacionales, con cobertura, fuentes e incertidumbre."><link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;600;700&display=swap" rel="stylesheet">')
 t=t.replace('<div class="eyebrow">Argentina · Inferencia ecológica</div><h1>¿De dónde vienen, hacia dónde van?</h1>','<h1>Electorados provinciales</h1>')
 t=t.replace('Electorados provinciales y elecciones nacionales. Explorá los flujos estimados sin perder de vista el territorio, las fuentes y la incertidumbre.','Explorá los flujos entre elecciones provinciales y nacionales, con sus fuentes e incertidumbre.')
 t=t.replace('<body><main>','<body><noscript><p>Activá JavaScript para explorar los Sankeys. <a href="LEEME.md">Consultar las fuentes y los datos</a>.</p></noscript><main>')
 t=t.replace('Provinciales → diputados 2025','Provinciales 2025')
 t=t.replace('class="chart-scroll"','class="chart-scroll" tabindex="0" role="region" aria-label="Sankey, desplazamiento horizontal en pantallas pequeñas"')
 t=t.replace('style="margin-top:24px"','style="margin-top:var(--space-lg)"')
 t=t.replace('Proyecto dataelecc · Elaboración local · Fuentes provinciales oficiales y DINE · Sin seguimiento individual','Proyecto dataelecc. Fuentes provinciales oficiales y DINE. Inferencia ecológica.')
 t=t.replace('Fuente provincial oficial ↗','Fuente provincial oficial')
 t=t.replace("const $=id=>document.getElementById(id), NS=", "const token=n=>getComputedStyle(document.documentElement).getPropertyValue('--'+n).trim();\nconst $=id=>document.getElementById(id), NS=")
 colors={
  '#27a249':'party-jsrn','#ce478b':'party-nosune','#14306e':'party-mpn','#7589bd':'party-mpn-aliados','#139b9b':'party-neuquinizate',
  '#294593':'party-frc','#d58b1f':'party-saenz','#9d3d74':'party-avancemos','#777d82':'party-bn','#949b9f':'party-blanco','#bcc4c8':'party-novoto','#a1a8a8':'party-otros',
  '#cc267b':'party-chaco','#6c4c98':'party-lla','#009ce4':'party-up','#e0b322':'party-jxc','#e14e57':'party-fit','#ed762b':'party-pu',
  '#2f3b81':'party-federal','#318ce7':'party-pj','#b94586':'party-potencia','#c54e3a':'party-corrientes','#23a393':'party-sanluis',
  '#c16b35':'party-alt-0','#437b6c':'party-alt-1','#9a658d':'party-alt-2','#6e852f':'party-alt-3','#b35162':'party-alt-4',
  '#54778c':'party-alt-5','#7368ae':'party-alt-6','#9c7b43':'party-alt-7','#468e9e':'party-alt-8','#8c633c':'party-alt-9',
  '#fff':'color-white','#172b36':'chart-ink','#537468':'chart-muted','#52666e':'chart-muted','#6f7f85':'chart-muted',
  '#243942':'chart-ink','#78858a':'chart-muted','#7c5a20':'chart-note',
 }
 for c,n in colors.items():t=t.replace("'"+c+"'","token('"+n+"')")
 t=t.replace('let W=1500,H=Math.max(830,','let W=1000,H=Math.max(760,')
 t=t.replace('top=170,bottom=105,gap=43,x0=330,x1=1150,nw=20','top=135,bottom=105,gap=43,x0=230,x1=740,nw=18')
 t=t.replace('function wrap(s,width=29)','function wrap(s,width=23)')
 old="add('text',{x:45,y:43,'font-size':14,fill:token('chart-muted'),'letter-spacing':2,'font-weight':650},'ELECTORADOS PROVINCIALES');"
 assert old in t
 t=t.replace(old,'')
 t=t.replace('x:45,y:84,\'font-size\':34','x:35,y:43,\'font-size\':27')
 t=t.replace('x:45,y:115,\'font-size\':15','x:35,y:73,\'font-size\':13')
 t=t.replace('y:148','y:111').replace('ORIGEN · EQUIVALENTES','Origen, equivalentes').replace('DESTINO · MODELO','Destino, modelo')
 t=t.replace('C 690 ${ya},790 ${yb}','C 430 ${ya},540 ${yb}').replace('C 790 ${yb+h},690 ${ya+h}','C 540 ${yb+h},430 ${ya+h}')
 t=t.replace("'font-weight':650","'font-weight':600")
 t=t.replace("svg.setAttribute('height',H);","svg.setAttribute('height',H);svg.setAttribute('font-family',token('font-body'));")
 t=t.replace("svg.setAttribute('font-family','Segoe UI, Arial, sans-serif');","svg.setAttribute('font-family',token('font-body'));")
 t=t.replace("'font-size':12,fill:token('chart-muted')","'font-size':12,fill:token('chart-muted')")
 # Metadata is a sentence, without decorative joins.
 t=t.replace(' · Fila','; fila').replace(' · '+"'+pct",'; '+"'+pct")
 t=t.replace('P05–P95','P05 a P95').replace('P05–P95','P05 a P95')
 t=t.replace("+'–'+fmt", "+' a '+fmt")
 t=t.replace('no seguimiento individual.','sin seguimiento individual.')
 t=t.replace('* Identificación insuficiente · Las cintas representan hipótesis, no seguimiento individual.','* Identificación insuficiente. Las cintas representan hipótesis, sin seguimiento individual.')
 t=t.replace("+' · '+", "+', '+")
 t=t.replace('} ${d.nivel} · Base:', '} ${d.nivel}. Base:').replace('${d.base} · Variante:', '${d.base}. Variante:')
 t=t.replace("node(i,'o')","node(i,'o')")
 t=t.replace("table.append(body)","table.append(body);let heads=[...table.querySelectorAll('thead th')].map(h=>h.innerText.replace(/\\s+/g,' '));table.querySelectorAll('tbody tr').forEach(r=>[...r.children].forEach((c,j)=>c.dataset.label=heads[j]||''))")
 t=t.replace('<button ', '<button type="button" ')
 path.write_text(t,encoding='utf8')
meta=HERE/'.hallmark';meta.mkdir(exist_ok=True)
(meta/'preflight.json').write_text(json.dumps(dict(
 scope='app',source='https://sankeydron.streamlit.app/',
 evidence=['transferencias/explorador/index.html:29-42: Ink, Epilogue, paper and reliability colours','.streamlit/config.toml:1-15: same Streamlit palette and face'],
 preserve=['all electoral data','all controls and exports','party colours','source and uncertainty notices'],
 introduce=['same Ink system','ruled workbench','compact status row','responsive labelled profile'],
 files=['transferencias/provinciales/visor.html','transferencias/provinciales/estilo.css','transferencias/provinciales/tokens.css','transferencias/provinciales/base.css'],
 material={'real':'25 calculated electoral crosses; official sources and audit tables','pictures':'the actual Sankey','absent':'photographs, invented metrics and decorative assets'},
 user_scope='Local viewer style; no change or deployment to the existing Streamlit app.'),ensure_ascii=False,indent=2),encoding='utf8')
print('Sistema Ink aplicado')
