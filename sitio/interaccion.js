/* rendimiento-v1: un cálculo por fotograma y ficha solo al cambiar de unidad. */
const tip=$("#tip");
let tipFrame=0,tipEvent=null,tipKey="",tipWidth=0,tipHeight=0;
let unitIndex=null;
function indexedUnit(i){
  if(!unitIndex){
    unitIndex=new Map();
    for(const e of mapEls){const k=+e.dataset.i;if(!unitIndex.has(k))unitIndex.set(k,[]);unitIndex.get(k).push(e);}
  }
  return unitIndex.get(i)||[];
}
function hideTip(){
  if(tipFrame)cancelAnimationFrame(tipFrame);tipFrame=0;tipEvent=null;
  tip.style.display="none";tipKey="";
}
function moveTip(){
  tipFrame=0;const ev=tipEvent;tipEvent=null;
  if(!ev||document.body.classList.contains("movil")||(DRAG&&DRAG.moved)){hideTip();return;}
  const t=ev.target.closest&&ev.target.closest("#B [data-i]");
  if(!t||!t.closest("#mainwrap")){hideTip();return;}
  const key=MODE+":"+t.dataset.i;
  if(key!==tipKey){
    tipKey=key;
    tip.innerHTML=cardHTML(viewFor({type:"unit",i:+t.dataset.i}),true)+`<div class="c-hint">clic: fijar los resultados</div>`;
    tip.style.left="0px";tip.style.top="0px";tip.style.display="block";
    tipWidth=tip.offsetWidth;tipHeight=tip.offsetHeight;
  }
  const tw=tipWidth,th=tipHeight;
  let x=Math.min(ev.clientX+16,innerWidth-tw-8);
  const y=Math.max(4,Math.min(ev.clientY+16,innerHeight-th-8));
  if(!card.hidden){
    const c=card.getBoundingClientRect();
    if(x<c.right&&x+tw>c.left&&y<c.bottom&&y+th>c.top)x=Math.max(4,ev.clientX-tw-16);
  }
  tip.style.transform=`translate(${Math.max(4,x)}px,${y}px)`;
}
// El plegado de fuerzas menores se ejecuta después de crear la ficha.
// Actualizar sus medidas también cuando ese observador cambia el contenido.
if(typeof ResizeObserver!=="undefined")new ResizeObserver(()=>{
  if(tip.style.display!=="none"){tipWidth=tip.offsetWidth;tipHeight=tip.offsetHeight;}
}).observe(tip);
svg.addEventListener("mousemove",ev=>{
  if(document.body.classList.contains("movil")||(DRAG&&DRAG.moved)){hideTip();return;}
  tipEvent={target:ev.target,clientX:ev.clientX,clientY:ev.clientY};
  if(!tipFrame)tipFrame=requestAnimationFrame(moveTip);
});
svg.addEventListener("mouseleave",hideTip);
svg.addEventListener("pointerdown",hideTip);
// Un desplazamiento del dedo no es un toque, incluso cuando el navegador
// intercepta el movimiento para desplazar la página sin zoom.
let touchTap=null;
svg.addEventListener("pointerdown",ev=>{
  if(ev.pointerType==="touch")touchTap={id:ev.pointerId,x:ev.clientX,y:ev.clientY,moved:false};
});
window.addEventListener("pointermove",ev=>{
  if(!touchTap||ev.pointerId!==touchTap.id||touchTap.moved)return;
  if(Math.hypot(ev.clientX-touchTap.x,ev.clientY-touchTap.y)>8){
    touchTap.moved=true;
    if(document.body.classList.contains("movil")&&SEL)clearSel();
  }
},true);
window.addEventListener("pointerup",ev=>{
  if(touchTap&&ev.pointerId===touchTap.id){
    if(touchTap.moved&&DRAG){DRAG.moved=true;}
    touchTap=null;
  }
},true);
window.addEventListener("pointercancel",()=>{touchTap=null;},true);
