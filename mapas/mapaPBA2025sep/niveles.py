"""Selector de nivel para la plantilla (generaliza el de ../mapaAMBA2025radios/build_amba2025radios.py y la serie 2005-2023).
levels = [(tecla, clase SVG, rótulo, título del botón, territories[].k)], el nivel base usa la clase «d» (y «dc» en recuadros de Capital).
Las unidades de los otros niveles van como <path class="<clase>" data-i=...> después de las del nivel base."""
import json


def nivel_patches(levels, default, extra_css=""):
    cls = [c for _, c, _, _, _ in levels if c != "d"]
    css = ",".join("." + c for c in cls) + "{stroke:#fff;stroke-linejoin:round;stroke-linecap:round;stroke-width:calc(var(--sd,2px) / var(--k,1))}\n"
    css += "".join(".%s{display:var(--v-%s,none)}" % (c, c) for c in cls)
    btn = "".join('<button data-n="%s"%s title="%s">%s</button>' % (k, ' class="on"' if k == default else "", t, lab) for k, _, lab, t, _ in levels)
    niv = "{" + ",".join('%s:["%s","%sc"]' % (k, c, c) for k, c, _, _, _ in levels) + "}"
    nivk = json.dumps({k: kn for k, _, _, _, kn in levels})
    nivof = json.dumps({kn: k for k, _, _, _, kn in levels})
    keys = "".join(k for k, _, _, _, _ in levels)
    return [
        ('.d{display:var(--v-d,none);stroke-width:calc(var(--sd,2px) / var(--k,1))}',
         '.d{display:var(--v-d,none);stroke-width:calc(var(--sd,2px) / var(--k,1))}\n' + css + "\n" + extra_css + "\n"
         '#niv button.on{background:#70a6d7;color:#111;border-color:#70a6d7}'),
        ('<span class="sp"></span>',
         '<div class="grp" id="niv" role="group" aria-label="Nivel del mapa"><span>Nivel:</span>' + btn + '</div><span class="sp"></span>'),
        ('let st=I.show.map(c=>`--v-${c}:inline`).join(";");', 'let st=I.show.map(c=>`--v-${nivCls(c)}:inline`).join(";");'),
        ('function selectUnit(i,zoom,pos){', 'function selectUnit(i,zoom,pos){if(T[i].k!==NIVK[NIVEL])setNivel(NIVOF[T[i].k]);'),
        ('M.units.forEach((u,i)=>{const row=', 'M.units.forEach((u,i)=>{if(T[i].k!==NIVK[NIVEL])return;const row='),
        ('drawTiles();drawTitle();renderCard();highlight();}',
         'drawTiles();drawTitle();renderCard();highlight();}\n'
         'const NIV=' + niv + ',NIVK=' + nivk + ',NIVOF=' + nivof + ';\n'
         'let NIVEL=((location.hash.match(/nv-([' + keys + '])/)||[])[1])||"' + default + '";\n'
         'function nivCls(c){return c==="d"?NIV[NIVEL][0]:c==="dc"?NIV[NIVEL][1]:c;}\n'
         'function setNivel(n){NIVEL=n;const mw=$("#mainwrap");if(mw.dataset.o==null)mw.dataset.o=mw.getAttribute("style");\n'
         '  mw.setAttribute("style",mw.dataset.o.replace(/--v-(dc|d):/g,(m,c)=>"--v-"+nivCls(c)+":"));drawInsets();\n'
         '  document.querySelectorAll("#niv button").forEach(b=>b.classList.toggle("on",b.dataset.n===n));\n'
         '  if(SEL&&SEL.type==="unit"&&T[SEL.i].k!==NIVK[n])clearSel();}'),
        ('const tip=$("#tip");', 'document.querySelectorAll("#niv button").forEach(b=>b.addEventListener("click",()=>setNivel(b.dataset.n)));\nconst tip=$("#tip");'),
        ('let DRAG=null,SEL=null;', 'let DRAG=null,SEL=null;\nsetNivel(NIVEL);'),
    ]
