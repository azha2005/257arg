"""Optimizaciones de interacción, solo para las copias de GitHub Pages.

Se aplican a la familia de la plantilla compartida, sin regenerar los atlas,
modificar sus datos ni cambiar el SVG descargado. Una plantilla incompatible
falla durante la publicación, en vez de dejar un visor parcialmente parcheado.
"""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
JS = (HERE / "interaccion.js").read_text(encoding="utf8")
MARCA = "/* rendimiento-v1 */"


def _una(texto, antes, despues):
    if texto.count(antes) != 1:
        raise ValueError(f"Parche de rendimiento incompatible: {antes[:100]!r}")
    return texto.replace(antes, despues, 1)


def optimizar(texto):
    if MARCA in texto or 'svg.addEventListener("mousemove",ev=>{' not in texto:
        return texto

    # El código corre en el mismo cierre que el atlas: conserva sus selectores,
    # modos internos, niveles y formatos de ficha específicos de cada elección.
    i = texto.index('const tip=$("#tip");')
    fin = 'svg.addEventListener("mouseleave",()=>tip.style.display="none");'
    j = texto.index(fin, i) + len(fin)
    texto = texto[:i] + JS + texto[j:]

    texto = _una(texto,
                'const f2=v=>new Intl.NumberFormat(LOC,{minimumFractionDigits:2,maximumFractionDigits:2}).format(v);',
                'const fmt2=new Intl.NumberFormat(LOC,{minimumFractionDigits:2,maximumFractionDigits:2});const f2=v=>fmt2.format(v);')
    texto = _una(texto, 'e.setAttribute("fill",c);e.style.stroke=sol?c:"";',
                'if(e.getAttribute("fill")!==c)e.setAttribute("fill",c);const stroke=sol?c:"";if(e.style.stroke!==stroke)e.style.stroke=stroke;')

    texto = _una(texto, 'function serialize(){', 'function serialize(){\n  settleZoom();setInsetDetail(true);')
    texto = _una(texto, 'const c=svg.cloneNode(true);', 'const c=svg.cloneNode(true);setInsetDetail();')
    texto = _una(texto, 'el("use",{href:"#B",style:st},s);',
                'const u=el("use",{"data-href":"#B",style:st},s);if(insetDetailVisible())u.setAttribute("href","#B");')
    texto = _una(texto, 'function drawInsets(){', '''function insetDetailVisible(){return location.hash.includes("bare")||!matchMedia("(max-width:760px)").matches||["rec","todo"].includes(document.body.dataset.vista);}
function setInsetDetail(force=false){for(const u of svg.querySelectorAll('#insets use[data-href]')){if(force||insetDetailVisible()){if(!u.hasAttribute("href"))u.setAttribute("href",u.dataset.href);}else u.removeAttribute("href");}}
function drawInsets(){''')
    texto = _una(texto, 'const dl=$("#c-list");dl.innerHTML=T.map((t,i)=>`<option value="${esc(t.n+" — "+t.p)}"></option>`).join("");',
                '''const dl=$("#c-list");let searchLabels=null,searchTimer=0;
  function searchOptions(){
    if(!searchLabels)searchLabels=T.map(t=>{const label=t.n+" — "+t.p;return [label,label.toLocaleLowerCase("es")];});
    const q=$("#c-find").value.trim().toLocaleLowerCase("es"),out=[];
    for(const [label,key] of searchLabels){if(!q||key.includes(q))out.push(`<option value="${esc(label)}"></option>`);if(out.length===60)break;}
    dl.innerHTML=out.join("");
  }
  $("#c-find").addEventListener("focus",searchOptions);
  $("#c-find").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(searchOptions,120);});''')
    texto = _una(texto, 'window.__atlas={setMode,get mode(){return MODE}',
                'window.__atlas={setInsetDetail,setMode,get zoom(){return Z.k},get mode(){return MODE}')
    texto = _una(texto, 'function applyZoom(){', '''let zoomFrame=0,lastStrokeScale=null,zoomSettleTimer=0;
function applyZoom(){
  if(mapEls.length>5000&&matchMedia("(max-width:760px)").matches&&!mw.classList.contains("en-movimiento"))mw.classList.add("en-movimiento");
  clearTimeout(zoomSettleTimer);zoomSettleTimer=setTimeout(settleZoom,160);
  if(!zoomFrame)zoomFrame=requestAnimationFrame(flushZoom);
}
function settleZoom(){clearTimeout(zoomSettleTimer);zoomSettleTimer=0;mw.classList.remove("en-movimiento");flushZoom();}
function flushZoom(){
  if(zoomFrame)cancelAnimationFrame(zoomFrame);zoomFrame=0;''')
    # Cambiar variables heredadas invalida el estilo de todos los radios.
    # Durante un arrastre solo cambia la traslación, no el grosor de línea.
    patron = r'  (mw\.style\.setProperty\("--sd",[^\n]+)'
    matches = list(re.finditer(patron, texto))
    if len(matches) != 1:
        raise ValueError("No se encontró el ajuste de grosor del zoom")
    m = matches[0]
    texto = texto[:m.start()] + '  if(lastStrokeScale!==Z.k&&(lastStrokeScale===null||!zoomSettleTimer)){lastStrokeScale=Z.k;' + m[1] + '}' + texto[m.end():]

    texto = _una(texto, 'const mainEls=i=>mapEls.filter(e=>+e.dataset.i===i&&e.closest("#mainwrap"));',
                'const mainEls=i=>indexedUnit(i).filter(e=>e.closest("#mainwrap"));')
    i = texto.index('function highlight(){')
    j = texto.index('function selectUnit(', i)
    texto = texto[:i] + '''let selectedEls=new Set(),dimmedEls=new Set(),highlightKey="";
function highlight(){
  const key=SEL?(SEL.type==="unit"?"u"+SEL.i:"p"+SEL.name):"";
  if(key===highlightKey)return;highlightKey=key;
  const nextSel=new Set(SEL&&SEL.type==="unit"?indexedUnit(SEL.i):[]);
  const nextDim=new Set(SEL&&SEL.type==="prov"?mapEls.filter(e=>T[+e.dataset.i].p!==SEL.name):[]);
  for(const e of selectedEls)if(!nextSel.has(e))e.classList.remove("sel");
  for(const e of dimmedEls)if(!nextDim.has(e))e.classList.remove("dim");
  for(const e of nextSel)if(!selectedEls.has(e)){e.classList.add("sel");if(e.parentNode)e.parentNode.appendChild(e);}
  for(const e of nextDim)if(!dimmedEls.has(e))e.classList.add("dim");
  selectedEls=nextSel;dimmedEls=nextDim;
}
''' + texto[j:]

    # Evitar que el gesto de arrastrar un rótulo active selección de texto.
    # El AMBA se extiende a la derecha del rectángulo del mapa nacional:
    # sus polígonos también deben responder al arrastre y a la rueda.
    texto = _una(texto, 'if(!inReg(x,y))return;ev.preventDefault();zoomAt(',
                'if(!inReg(x,y)&&!(ev.target.closest&&ev.target.closest("#mainwrap")))return;ev.preventDefault();zoomAt(')
    texto = _una(texto, 'if(ev.button!==0||!inReg(x,y))return;DRAG=',
                'if(ev.button!==0||(!inReg(x,y)&&!(ev.target.closest&&ev.target.closest("#mainwrap"))))return;DRAG=')
    texto = _una(texto, 'DRAG={x,y,tx:Z.tx,ty:Z.ty,moved:false,',
                'if(ev.pointerType!=="touch")ev.preventDefault();DRAG={matrix:svg.getScreenCTM().inverse(),id:ev.pointerId,x,y,tx:Z.tx,ty:Z.ty,moved:false,')
    texto = _una(texto, 'const [x,y]=toPoster(ev);Z.tx=DRAG.tx+',
                'const pt=new DOMPoint(ev.clientX,ev.clientY).matrixTransform(DRAG.matrix),x=pt.x,y=pt.y;Z.tx=DRAG.tx+')
    texto = _una(texto, 'window.addEventListener("pointermove",ev=>{if(!DRAG)return;',
                'window.addEventListener("pointermove",ev=>{if(!DRAG||DRAG.id!==ev.pointerId)return;')
    texto = _una(texto, 'DRAG.moved=true;svg.classList.add("pan");',
                'if(!DRAG.moved){DRAG.moved=true;svg.classList.add("pan");}')
    texto = _una(texto, 'window.addEventListener("pointerup",ev=>{if(!DRAG)return;',
                'window.addEventListener("pointerup",ev=>{if(!DRAG||DRAG.id!==ev.pointerId)return;')
    texto = _una(texto, '$("#z-in").addEventListener', '''window.addEventListener("pointercancel",ev=>{if(DRAG&&DRAG.id===ev.pointerId){DRAG=null;svg.classList.remove("pan");}});
window.addEventListener("blur",()=>{DRAG=null;svg.classList.remove("pan");});
svg.addEventListener("touchstart",ev=>{if(ev.touches.length>1){DRAG=null;svg.classList.remove("pan");}},{passive:true,capture:true});
$("#z-in").addEventListener''')
    texto = _una(texto, '</head>', '''<style>/* rendimiento-v1 */
#atlas,#atlas text{-webkit-user-select:none;user-select:none}
#tip{will-change:transform}
#mainwrap.en-movimiento :is(.d,.dc,.rcb,.rcc,.ck,.ckc){stroke:none!important}
</style></head>''')
    return texto
