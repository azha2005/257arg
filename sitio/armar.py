"""Sitio de GitHub Pages con todos los atlas (2-nov-2026).

    python sitio/armar.py miniaturas [filtro]   # capturas en sitio/miniaturas/ (Chrome con Playwright)
    python sitio/armar.py indice               # sitio/index.html desde catalogo.py
    python sitio/armar.py copiar _site         # arma el sitio (lo corre el workflow .github/workflows/pages.yml)

El índice sigue el estilo Ink de transferencias/provinciales/INDICE.html, con modo oscuro.
"""
import glob, html, io, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalogo import GRUPOS, EXTRA, MINI, CRUDOS
from rendimiento import optimizar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "sitio")
MINIS = os.path.join(HERE, "miniaturas")


def entradas():
    for g in GRUPOS:
        for e in g[3]: yield e


def mini_nombre(ruta):
    return ruta.replace("mapas/", "").replace("/", "__").replace(".html", ".webp")


def miniaturas(filtro=""):
    """Dos capturas del póster (#atlas, sin la barra): fondo negro y fondo blanco, como el modo del índice."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(MINIS, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1920, "height": 1700})
        for ruta, *_ in entradas():
            if filtro not in ruta: continue
            src = MINI.get(ruta, ruta)
            for hash_, suf in (("#bare", ""), ("#bare-white", "_claro")):
                pg.goto("about:blank")
                pg.goto("file:///" + os.path.join(ROOT, src).replace(os.sep, "/") + hash_)
                pg.wait_for_timeout(2500)
                im = Image.open(io.BytesIO(pg.locator("#atlas").screenshot())).convert("RGB")
                im.thumbnail((640, 640), Image.LANCZOS)
                im.save(os.path.join(MINIS, mini_nombre(ruta).replace(".webp", suf + ".webp")), "WEBP", quality=72, method=6)
            print(ruta, flush=True)
        b.close()


CSS = open(os.path.join(HERE, "estilo.css"), encoding="utf8").read()


def indice():
    n = sum(1 for _ in entradas())
    corto = {"2003-2025": "2003–2025", "amba": "AMBA", "escenarios": "Escenarios"}   # la barra entra en una línea
    nav = "".join(f'<a href="#{gid}">{html.escape(corto.get(gid, t.split(",")[0]))}</a>' for gid, t, _, _ in GRUPOS)
    secs = []
    for gid, titulo, bajada, items in GRUPOS:
        cards = []
        for ruta, anio, rot, nota in items:
            m = mini_nombre(ruta)
            ok = os.path.exists(os.path.join(MINIS, m))
            mc = m.replace(".webp", "_claro.webp")
            img = ((f'<img class="osc" src="miniaturas/{m}" alt="" loading="lazy" width="640" height="550">'
                    f'<img class="cla" src="miniaturas/{mc}" alt="" loading="lazy" width="640" height="550">') if ok else "")
            nota_h = f'<span class="nota">{html.escape(nota)}</span>' if nota else ""
            cards.append(f'<li><a class="atlas" href="{ruta}"><span class="mini">{img}</span>'
                         f'<span class="anio num">{anio}</span><span class="rot">{html.escape(rot)}</span>{nota_h}</a></li>')
        secs.append(f'<section id="{gid}" aria-labelledby="h-{gid}"><div class="cab"><h2 id="h-{gid}">{html.escape(titulo)}</h2>'
                    f'<p>{html.escape(bajada)}</p></div><ul class="grilla">{"".join(cards)}</ul></section>')
    out = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas electorales argentinos</title>
<meta name="description" content="{n} atlas electorales de la Argentina por departamento, circuito y radio censal, de 1912 a 2025, al estilo de los mapas de la Wikipedia.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://azha2005.github.io/257arg/">
<meta property="og:title" content="Atlas electorales de la Argentina, 1912–2025">
<meta property="og:description" content="{n} atlas: elecciones por departamento de 1912 a 2025, PASO incluidas, y el AMBA radio por radio.">
<meta property="og:image" content="https://azha2005.github.io/257arg/vista_previa.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Cuatro atlas electorales: 1928, 1946, PASO 2023 y AMBA 2025 por radio censal">
<meta property="og:locale" content="es_AR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://azha2005.github.io/257arg/vista_previa.png">
<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;600;700&display=swap" rel="stylesheet">
<script>try{{const t=localStorage.getItem("tema");if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<style>
{CSS}</style></head>
<body>
<header class="tope"><div class="container fila"><a class="marca" href="./">Atlas electorales</a>
<nav aria-label="Secciones">{nav}</nav>
<button type="button" class="tema" id="tema" aria-label="Cambiar entre modo claro y oscuro">Modo oscuro</button></div></header>
<main>
<section class="hero container"><h1>Cómo votó la Argentina, departamento por departamento</h1>
<p class="lead">{n} atlas interactivos de 1912 a 2025, al estilo Wikipedia.</p>
<p class="acc"><a class="btn" href="#1912-1930">Ver los atlas</a></p></section>
<div class="container">{"".join(secs)}</div>
</main>
<footer class="pie"><div class="container">
<p>Cada atlas es un HTML autocontenido: pestañas por modo, ficha de cada unidad y descarga en SVG o PNG. Lo que falta queda en beige y rotulado; no se imputa.</p>
<p>Fuentes: Darío Cantón, base de Ernesto Calvo, Lupu y Stokes, DINE, PolAr (Andy Tow), CNE, Wikipedia. Cartografía de Rodríguez (CEUR-CONICET), CC BY 2.5 Argentina. Código y datos en <a href="https://github.com/azha2005/257arg">github.com/azha2005/257arg</a>.</p>
<p>Hecho por azhadron / elfiguretti / itsahardlife.</p>
</div></footer>
<script>
(function(){{const b=document.getElementById("tema"),r=document.documentElement;
function oscuro(){{return r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;}}
function rot(){{b.textContent=oscuro()?"Modo claro":"Modo oscuro";}}
b.addEventListener("click",function(){{r.dataset.theme=oscuro()?"light":"dark";try{{localStorage.setItem("tema",r.dataset.theme);}}catch(e){{}}rot();}});rot();}})();
</script>
</body></html>
"""
    open(os.path.join(HERE, "index.html"), "w", encoding="utf8", newline="\n").write(out)
    print("index.html,", n, "entradas")


# Solo en la copia publicada (los HTML del repo no cambian): enlace al índice, la nota de fuentes plegada
# y el modo claro u oscuro que eligió el visitante en el índice (localStorage «tema», el mismo origen).
SITIO_CSS = ('<style>/*sitio*/#bar a.sitio-ind{color:var(--ctlfg);text-decoration:none;font-weight:600;padding:4px 6px}'
             '#bar a.sitio-ind:hover{text-decoration:underline}'
             '#barnote-d{flex-basis:100%;order:9;color:var(--mut);font-size:13px}'
             '#barnote-d summary{cursor:pointer;width:max-content}#barnote-d #barnote{margin-top:4px}#barnote-d .sitio-autor{margin:6px 0 0}'
             'body.sin-rec #insets>:not(.keep):not(#cababub){display:none}</style>\n')
SITIO_JS = ('<script>/*sitio*/(function(){var b=document.body,bar=document.getElementById("bar"),n=document.getElementById("barnote");'
            'if(bar){var a=document.createElement("a");a.className="sitio-ind";a.href="../../";a.textContent="Todos los atlas";'
            'bar.insertBefore(a,bar.firstChild);}'
            'if(n){var d=document.createElement("details");d.id="barnote-d";var s=document.createElement("summary");'
            's.textContent="Fuentes y notas";d.appendChild(s);n.parentNode.insertBefore(d,n);d.appendChild(n);var hc=document.createElement("p");hc.className="sitio-autor";hc.textContent="Hecho por azhadron / elfiguretti / itsahardlife.";d.appendChild(hc);}'
            'var t=null;try{t=localStorage.getItem("tema");}catch(e){}'
            'var claro=t?t==="light":matchMedia("(prefers-color-scheme: light)").matches;'
            'if(claro&&location.hash.indexOf("bare")<0){b.dataset.bg="white";var g=document.getElementById("b-bg");if(g)g.textContent="Fondo: blanco";}'
            # el póster entero a la vista: el ancho se limita para que quepa en el alto de la ventana (con la barra)
            'var sv=document.getElementById("atlas"),w=document.getElementById("wrap");'
            'function fit(){if(!sv||!w||location.hash.indexOf("bare")>=0||document.body.classList.contains("movil"))return;var vb=sv.viewBox&&sv.viewBox.baseVal;if(!vb||!vb.height)return;'
            'var bh=bar?bar.offsetHeight:0;w.style.maxWidth=Math.max(760,Math.min(1920,(innerHeight-bh-28)*vb.width/vb.height))+"px";}'
            'fit();addEventListener("resize",fit);'
            # botón para ocultar los recuadros (se recuerda en este navegador)
            'var bg=document.getElementById("b-bg"),ins=document.getElementById("insets");'
            'if(ins)[].forEach.call(ins.querySelectorAll("text.lbl"),function(t){if(/^Provincias/.test(t.textContent))t.classList.add("keep");});'
            'if(bg&&ins){var r=document.createElement("button");r.id="b-rec";r.type="button";'
            'function rr(){r.textContent=b.classList.contains("sin-rec")?"Mostrar recuadros":"Ocultar recuadros";}'
            'try{if(localStorage.getItem("recuadros")==="no")b.classList.add("sin-rec");}catch(e){}'
            'r.addEventListener("click",function(){var o=b.classList.toggle("sin-rec");try{localStorage.setItem("recuadros",o?"no":"si");}catch(e){}rr();window.__huecos();});'
            'rr();bg.parentNode.insertBefore(r,bg);}'
            # el mapa principal se recorta con huecos donde van los recuadros: sin recuadros, el hueco quedaría vacío
            'var cp=document.getElementById("clippath"),cpd=cp&&cp.getAttribute("d");'
            'window.__huecos=function(){if(!cp)return;var v=b.dataset.vista,sin=b.classList.contains("sin-rec")||(b.classList.contains("movil")&&v!=="rec"&&v!=="todo");'
            'cp.setAttribute("d",sin?cpd.replace(/ M[\\s\\S]*$/,""):cpd);};window.__huecos();'
            # la ficha no repite la nota general del modo (está en «Fuentes y notas»); quedan las notas propias de la unidad
            'function sinNota(c){if(!c)return;'
            'new MutationObserver(function(){var bn=document.getElementById("barnote"),g=bn?bn.textContent.trim():"";c.querySelectorAll(".c-note").forEach(function(n){var t=n.textContent;'
            'if(g&&t.indexOf(g)>=0){t=t.replace(" · "+g,"").replace(g,"").trim();if(t)n.textContent=t;else n.remove();}});})'
            '.observe(c,{childList:true,subtree:true});}'
            'sinNota(document.getElementById("card"));sinNota(document.getElementById("tip"));'
            # con muchas fuerzas (1965, PASO…) la ficha junta las menores al 2 % desde la 7.ª en «Otras N fuerzas», que se despliega
            'var BN=/blanc|nul|impugn|recurr|no vot|bronca/i;function pc(r){var e=r.querySelector(".pc");return e?parseFloat(e.textContent.replace(/\\./g,"").replace(",","."))||0:0}'
            'function plegar(c,tip){if(c.querySelector(".c-mas"))return;var t=c.querySelector(".c-title"),k=t?t.textContent:"";if(c.dataset.todas===k)return;'
            'var par=[].slice.call(c.querySelectorAll(".c-row")).filter(function(r){var n=r.querySelector(".nm");return n&&!BN.test(n.textContent)});if(par.length<10)return;'
            'var esc=par.filter(function(r,i){return i>=6&&pc(r)<2});if(esc.length<3)return;var tot=0;esc.forEach(function(r){tot+=pc(r);r.classList.add("c-esc")});'
            'var m=document.createElement("div");m.className="c-row c-mas";m.innerHTML=\'<span class="nm"><i style="background:#bdbdbd"></i>Otras \'+esc.length+\' fuerzas\'+(tip?"":\' <u>ver todas</u>\')+\'</span><span class="pc">\'+tot.toFixed(2).replace(".",",")+\' %</span><span class="vt"></span>\';'
            'esc[0].parentNode.insertBefore(m,esc[0]);if(!tip)m.addEventListener("click",function(ev){ev.stopPropagation();c.dataset.todas=k;esc.forEach(function(r){r.classList.remove("c-esc")});m.remove();});}'
            'function vigilar(c,tip){if(!c)return;plegar(c,tip);new MutationObserver(function(){plegar(c,tip)}).observe(c,{childList:true,subtree:true});}'
            'vigilar(document.getElementById("card"),false);vigilar(document.getElementById("tip"),true);'
            'var cs=document.createElement("style");cs.textContent=".c-esc{display:none!important}.c-mas{cursor:pointer}.c-mas u{font-weight:400;opacity:.7;margin-left:4px}#tip .c-mas{cursor:default}";document.head.appendChild(cs);'
            '})();</script>\n')

# Modo celular (pantallas de hasta 760 px): el póster de 1920 px no se lee achicado, así que se muestra por partes
# (mapa, resultados, recuadros o el póster entero) cambiando el viewBox del mismo SVG; los modos pasan a un
# selector, el resto de la barra a «Más», la ficha sale desde abajo y el mapa se acerca con dos dedos.
MOVIL_CSS = ('<style>/*movil*/#m-row,#m-cab{display:none}'
             'body.movil #bar{padding:6px 10px;gap:6px}'
             'body.movil:not(.m-mas) #bar>*:not(#m-row){display:none!important}'
             'body.movil #bar .grp{flex-wrap:wrap}body.movil #c-find{width:100%;min-width:0;box-sizing:border-box}'
             'body.movil #m-row{display:flex;gap:6px;width:100%;align-items:center}'
             'body.movil #m-row select{flex:1;min-width:0;padding:7px 8px}body.movil #m-row button{padding:7px 12px}'
             'body.movil #m-row a.sitio-ind{padding:4px 2px;white-space:nowrap}'
             'body.movil #m-cab{display:block;padding:4px 10px 0;color:var(--fg);font-size:15px;font-weight:700;line-height:1.2}'
             'body.movil #m-cab small{display:block;color:var(--mut);font-weight:400;font-size:12.5px}'
             '#m-vis{display:flex;gap:4px;margin:8px 0 2px}#m-vis button{flex:1;font:inherit;font-size:13px;font-weight:400;padding:6px 0;'
             'color:var(--ctlfg);background:var(--ctl);border:1px solid var(--line);border-radius:3px}'
             '#m-vis button.on{border-color:#70a6d7;font-weight:700}'
             '#m-rq{display:none;gap:4px;overflow-x:auto;scrollbar-width:none;margin-top:4px}body.movil[data-vista="rec"] #m-rq{display:flex}'
             '#m-rq button{flex:none;font:inherit;font-size:12.5px;padding:5px 9px;color:var(--ctlfg);background:var(--ctl);border:1px solid var(--line);border-radius:14px;white-space:nowrap}'
             '#m-rq button.on{border-color:#70a6d7;font-weight:700}'
             'body.movil:not([data-vista="mapa"]) #atlas{height:auto;max-height:calc(100svh - var(--mh,150px));margin:0 auto}'
             'body.movil #card .c-title{font-size:19px}body.movil #card .c-sec{font-size:13px}body.movil #card .c-row{grid-template-columns:1fr 58px 76px;font-size:14px}'
             'body.movil #wrap{padding:0 0 10px;max-width:none!important}'
             'body.movil[data-vista="mapa"] #atlas{height:calc(100svh - var(--mh,150px));width:min(100%,calc((100svh - var(--mh,150px))*var(--ar,.545)));margin:0 auto;touch-action:pan-y}'
             'body.movil[data-vista="mapa"] #insets>:not(.keep):not(#cababub),body.movil[data-vista="res"] #insets>:not(.keep):not(#cababub){display:none}'
             'body.movil[data-vista="rec"] #insets>*{display:inline!important}'
             'body.movil #tip{display:none!important}'
             'body.movil #card{left:0!important;right:0;top:auto!important;bottom:0;width:auto;max-height:min(32svh,calc((100svh - var(--mh,150px)) * .42));overscroll-behavior:contain;touch-action:pan-y;'
             'border-radius:12px 12px 0 0;box-sizing:border-box;padding-bottom:max(12px,env(safe-area-inset-bottom))}'
             'body.movil #card-x{min-width:44px;min-height:44px;top:0;right:0}'
             'body.movil #card.arriba{top:var(--ct,0px)!important;bottom:auto;border-radius:0 0 12px 12px;padding-bottom:12px}</style>\n')
MOVIL_JS = ('<script>/*movil*/(function(){var sv=document.getElementById("atlas"),bar=document.getElementById("bar"),b=document.body;'
            'if(!sv||!bar||typeof DATA==="undefined"||location.hash.indexOf("bare")>=0)return;'
            'var mq=matchMedia("(max-width: 760px)"),VB0=sv.getAttribute("viewBox"),vista="mapa",hecho=false;'
            'var R=(typeof REG!=="undefined")?REG:{x:570,y:100,w:840,h:1540};''b.style.setProperty("--ar",(R.w/R.h).toFixed(4));'
            'function nom(m){var t=m.tile||m.id;if(m.label)return m.label;if(/^GAN/i.test(t))return "Ganó";if(/^PART/i.test(t))return "Participación";'
            'if(/^I-/.test(t))return "Interna "+t.slice(2);return "% "+t;}'
            # caja (en coordenadas del póster) de un conjunto de elementos, medida con el póster entero
            'function caja(sels){var m=sv.getScreenCTM();if(!m)return null;m=m.inverse();var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;'
            'sels.forEach(function(s){sv.querySelectorAll(s).forEach(function(e){var r=e.getBoundingClientRect();if(!r.width||!r.height)return;'
            '[[r.left,r.top],[r.right,r.bottom]].forEach(function(c){var p=new DOMPoint(c[0],c[1]).matrixTransform(m);'
            'x0=Math.min(x0,p.x);y0=Math.min(y0,p.y);x1=Math.max(x1,p.x);y1=Math.max(y1,p.y);});});});'
            'return x1>x0?[x0-12,y0-12,x1-x0+24,y1-y0+24].map(function(v){return v.toFixed(1)}).join(" "):null;}'
            # recuadros: cada rótulo con su marco (o, sin marco, el mapa que lo sigue); se muestran de a uno
            'function cajaDe(e){var m=sv.getScreenCTM().inverse(),r=e.getBoundingClientRect(),a=new DOMPoint(r.left,r.top).matrixTransform(m),z=new DOMPoint(r.right,r.bottom).matrixTransform(m);return [a.x,a.y,z.x,z.y];}'
            'function recuadros(){var ins=sv.querySelector("#insets");if(!ins)return [];var out=[],fr=[].slice.call(ins.querySelectorAll(":scope>rect.frame")).map(cajaDe);'
            '[].slice.call(ins.querySelectorAll(":scope>text.lbl")).forEach(function(t){var l=cajaDe(t),bx=null;'
            'fr.forEach(function(f){if(!bx&&f[1]>=l[3]-8&&f[1]-l[3]<40&&f[0]<l[2]&&f[2]>l[0])bx=f;});'
            'if(!bx){var s=t.nextElementSibling,p=t.previousElementSibling;[p,s].forEach(function(e){if(!bx&&e&&e.tagName==="svg"){var c=cajaDe(e);if(c[2]-c[0]<700&&c[0]>=0&&c[3]<=1700&&Math.abs(c[1]-l[3])<60)bx=c;}});}'
            'if(bx)out.push({n:t.textContent,v:[Math.min(l[0],bx[0])-10,l[1]-10,Math.max(l[2],bx[2])-Math.min(l[0],bx[0])+20,bx[3]-l[1]+20]});});return out;}'
            'var RQ=[],rq=0;'
            'function poner(v){vista=v;b.dataset.vista=v;if(window.__atlas&&window.__atlas.setInsetDetail)window.__atlas.setInsetDetail();sv.setAttribute("viewBox",VB0);var vb=VB0;'
            'if(v==="mapa")vb=R.x+" "+R.y+" "+R.w+" "+R.h;'
            'else if(v==="res")vb=caja(["#pie","#legend","#pv"])||VB0;'
            'else if(v==="rec"){RQ=recuadros();var ch=document.getElementById("m-rq");ch.replaceChildren();'
            'RQ.forEach(function(q,i){var x=document.createElement("button");x.type="button";x.textContent=q.n;x.className=i===rq?"on":"";'
            'x.addEventListener("click",function(){rq=i;poner("rec");});ch.appendChild(x);});'
            'if(RQ[rq])vb=RQ[rq].v.map(function(n){return n.toFixed(1)}).join(" ");}'
            'sv.setAttribute("viewBox",vb);var q=vb.split(/[ ,]+/).map(Number);sv.style.aspectRatio=v==="mapa"?"":(q[2]/q[3]).toFixed(4);'
            'document.querySelectorAll("#m-vis button").forEach(function(x){x.classList.toggle("on",x.dataset.v===v)});alto();if(window.__huecos)window.__huecos();if(window.__tacto)window.__tacto();}'
            'function alto(){var w=document.getElementById("wrap");var t=w?w.getBoundingClientRect().top+scrollY:150;b.style.setProperty("--mh",(t+12)+"px");}'
            'function cab(){var c=document.getElementById("m-cab");if(!c)return;var s=document.getElementById("sub"),st=s&&s.getAttribute("display")!=="none"?s.textContent:"";'
            'c.firstChild.textContent=(DATA.title||"")+" "+(DATA.year||"");c.querySelector("small").textContent=st;'
            'var sel=document.getElementById("m-modo");if(sel&&window.__atlas)sel.value=window.__atlas.mode;}'
            'function armar(){if(hecho)return;hecho=true;'
            'var row=document.createElement("div");row.id="m-row";var ind=bar.querySelector("a.sitio-ind");'
            'var sel=document.createElement("select");sel.id="m-modo";sel.setAttribute("aria-label","Modo del mapa");'
            'var sets=DATA.sets||{};var grupos={};DATA.modes.forEach(function(m){var k=m.set||"1";(grupos[k]=grupos[k]||[]).push(m);});'
            'Object.keys(grupos).forEach(function(k){var par=sel;if(Object.keys(grupos).length>1){par=document.createElement("optgroup");par.label=(sets[k]&&sets[k].label)||k;sel.appendChild(par);}'
            'grupos[k].forEach(function(m){var o=document.createElement("option");o.value=m.id;o.textContent=nom(m);par.appendChild(o);});});'
            'sel.addEventListener("change",function(){window.__atlas&&window.__atlas.setMode?window.__atlas.setMode(sel.value):setMode(sel.value);});'
            'var mas=document.createElement("button");mas.type="button";mas.textContent="Más";mas.setAttribute("aria-expanded","false");'
            'mas.addEventListener("click",function(){var o=b.classList.toggle("m-mas");mas.setAttribute("aria-expanded",o);mas.textContent=o?"Menos":"Más";alto();});'
            'if(ind)row.appendChild(ind);row.appendChild(sel);row.appendChild(mas);bar.insertBefore(row,bar.firstChild);'
            'var c=document.createElement("div");c.id="m-cab";c.appendChild(document.createTextNode(""));c.appendChild(document.createElement("small"));'
            'var vis=document.createElement("div");vis.id="m-vis";[["mapa","Mapa"],["res","Resultados"],["rec","Recuadros"],["todo","Póster"]].forEach(function(p){'
            'var x=document.createElement("button");x.type="button";x.dataset.v=p[0];x.textContent=p[1];x.addEventListener("click",function(){poner(p[0]);});vis.appendChild(x);});'
            'c.appendChild(vis);var ch=document.createElement("div");ch.id="m-rq";c.appendChild(ch);bar.parentNode.insertBefore(c,bar.nextSibling);'
            # el código del atlas está encapsulado: se observa el SVG en vez de envolver sus funciones.
            # Ficha: arriba si la unidad tocada queda en la mitad de abajo de la pantalla, abajo si no.
            'var cd=document.getElementById("card");'
            'function ubicar(){if(!cd||cd.hidden||!b.classList.contains("movil"))return;var y0=1e9,y1=-1e9;'
            'sv.querySelectorAll("#mainwrap .sel").forEach(function(e){var r=e.getBoundingClientRect();y0=Math.min(y0,r.top);y1=Math.max(y1,r.bottom);});'
            'var hc=document.getElementById("m-cab");b.style.setProperty("--ct",Math.max(0,hc?hc.getBoundingClientRect().bottom+4:0)+"px");'
            'cd.classList.toggle("arriba",y1>y0&&(y0+y1)/2>innerHeight*0.5);}'
            'if(cd)new MutationObserver(function(){requestAnimationFrame(ubicar);}).observe(cd,{attributes:true,childList:true,subtree:true});'
            # al cambiar de modo cambian el subtítulo y la leyenda: encabezado y vista se vuelven a armar
            'var t0=null;new MutationObserver(function(){clearTimeout(t0);t0=setTimeout(function(){cab();if(b.classList.contains("movil")&&vista!=="mapa")poner(vista);},60);})'
            '.observe(sv.querySelector("#legend")||sv,{childList:true});'
            # dos dedos: acercar (la escala se lee del transform del mapa); con un dedo el atlas ya arrastra
            'var zg=sv.querySelector("#zoomg"),dedos=new Set(),P=null,pinchMatrix=null;'
            'function esc(){if(window.__atlas&&window.__atlas.zoom!=null)return window.__atlas.zoom;var m=/scale\\(([\\d.]+)\\)/.exec(zg&&zg.getAttribute("transform")||"");return m?+m[1]:1;}'
            'function mid(e){var a=e.touches[0],z=e.touches[1];return {x:(a.clientX+z.clientX)/2,y:(a.clientY+z.clientY)/2,d:Math.hypot(a.clientX-z.clientX,a.clientY-z.clientY)};}'
            'function pp(q){var m=pinchMatrix||sv.getScreenCTM().inverse();var p=new DOMPoint(q.x,q.y).matrixTransform(m);return [p.x,p.y];}'
            'addEventListener("pointerdown",function(e){if(e.pointerType==="touch")dedos.add(e.pointerId);},true);'
            '["pointerup","pointercancel"].forEach(function(t){addEventListener(t,function(e){dedos.delete(e.pointerId);},true);});'
            # con dos dedos (y hasta levantarlos todos) el arrastre del atlas no recibe los movimientos
            # sin acercar, un dedo desplaza la página (no arrastra el mapa); acercado, arrastra el mapa
            'function tacto(){var a=b.classList.contains("movil")&&vista==="mapa"&&esc()>1.01?"none":"";if(sv.style.touchAction!==a)sv.style.touchAction=a;}'
            'window.__tacto=tacto;if(zg)new MutationObserver(tacto).observe(zg,{attributes:true,attributeFilter:["transform"]});'
            'addEventListener("pointermove",function(e){if(e.pointerType==="touch"&&(dedos.size>1||P||cortar||(vista==="mapa"&&esc()<=1.01)))e.stopImmediatePropagation();},true);var cortar=false;'
            'sv.addEventListener("touchstart",function(e){if(!b.classList.contains("movil")||vista!=="mapa"||e.touches.length!==2||!window.__atlas)return;P=mid(e);pinchMatrix=sv.getScreenCTM().inverse();cortar=true;e.preventDefault();},{passive:false});'
            'sv.addEventListener("touchmove",function(e){if(!P||e.touches.length!==2)return;e.preventDefault();var q=mid(e),c=pp(q);'
            'window.__atlas.zoomAt(c[0],c[1],esc()*q.d/Math.max(1,P.d));P=q;},{passive:false});'
            'sv.addEventListener("touchend",function(e){if(e.touches.length<2){P=null;pinchMatrix=null;}if(!e.touches.length)cortar=false;});'
            'cab();}'
            'function aplicar(){if(mq.matches){armar();b.classList.add("movil");poner(vista);var w=document.getElementById("wrap");if(w)w.style.maxWidth="";}'
            'else if(hecho){b.classList.remove("movil","m-mas");delete b.dataset.vista;if(window.__atlas&&window.__atlas.setInsetDetail)window.__atlas.setInsetDetail();sv.setAttribute("viewBox",VB0);dispatchEvent(new Event("resize"));}}'
            'aplicar();mq.addEventListener("change",aplicar);addEventListener("resize",function(){if(b.classList.contains("movil"))alto();});'
            '})();</script>\n')


def preparar(html):
    if "/*sitio*/" in html or '<div id="bar">' not in html: return html
    html = optimizar(html)
    html = html.replace("</head>", SITIO_CSS + MOVIL_CSS + "</head>", 1)
    i = html.rindex("</body>") if "</body>" in html else len(html)
    return html[:i] + SITIO_JS + MOVIL_JS + html[i:]


def copiar(dest):
    rutas = [e[0] for e in entradas()]
    for pat in EXTRA: rutas += [os.path.relpath(f, ROOT).replace(os.sep, "/") for f in glob.glob(os.path.join(ROOT, pat))]
    os.makedirs(dest, exist_ok=True)
    shutil.copy(os.path.join(HERE, "index.html"), dest)
    shutil.copy(os.path.join(HERE, "vista_previa.png"), dest)   # imagen de la tarjeta del enlace (og:image)
    shutil.copytree(MINIS, os.path.join(dest, "miniaturas"), dirs_exist_ok=True)
    open(os.path.join(dest, ".nojekyll"), "w").close()
    tot = 0
    for r in sorted(set(rutas)):
        d = os.path.join(dest, r); os.makedirs(os.path.dirname(d), exist_ok=True)
        s = open(os.path.join(ROOT, r), encoding="utf8").read()
        open(d, "w", encoding="utf8", newline="").write(preparar(s)); tot += os.path.getsize(d)
    for r in CRUDOS:
        d = os.path.join(dest, r); os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy(os.path.join(ROOT, r), d); tot += os.path.getsize(d)
    print(len(set(rutas)) + len(CRUDOS), "HTML,", round(tot / 2**20), "MB")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "miniaturas": miniaturas(sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "indice": indice()
    elif cmd == "copiar": copiar(sys.argv[2])
