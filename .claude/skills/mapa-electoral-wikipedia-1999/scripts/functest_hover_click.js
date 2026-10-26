// Prueba con detección de elemento REAL: se busca lo que hay bajo el punto (elementFromPoint) y el evento se
// envía a ESE elemento, como haría el navegador con un mouse.
window.addEventListener('error',e=>{document.body.setAttribute('data-t','ERR '+e.message)});
setTimeout(()=>{
 try{
  const out={};const NL=String.fromCharCode(10);
  const T=DATA.territories;
  const center=(n,p)=>{const i=T.findIndex(t=>t.n===n&&(!p||t.p===p));const el=document.querySelector('#mainwrap #B path.d[data-i="'+i+'"]');const r=el.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2,i];};
  const fire=(el,type,x,y,Cls)=>el.dispatchEvent(new (Cls||MouseEvent)(type,{bubbles:true,clientX:x,clientY:y,button:0}));
  // puntos candidatos dentro de Rosario (el centro de la caja puede caer fuera del polígono): se busca uno que pertenezca al departamento
  function hit(n,p){
    const i=T.findIndex(t=>t.n===n&&(!p||t.p===p));const els=[...document.querySelectorAll('#mainwrap #B path.d[data-i="'+i+'"]')];
    for(const el of els){const r=el.getBoundingClientRect();
      for(let a=1;a<12;a++)for(let b=1;b<12;b++){const x=r.left+r.width*a/12,y=r.top+r.height*b/12;const t=document.elementFromPoint(x,y);
        if(t&&t.closest&&+t.dataset.i===i)return [x,y,t];}}
    return null;
  }
  const h1=hit('Rosario','Santa Fe');out.rosarioHit=h1?h1[2].tagName+'#'+h1[2].id+'.'+h1[2].getAttribute('class'):'NO ENCONTRADO';
  // quién está encima de un punto cualquiera del mapa, sin mirar el departamento
  const mid=document.elementFromPoint(h1?h1[0]:900,h1?h1[1]:700);out.topAtPoint=mid.tagName+'#'+(mid.id||'')+'.'+(mid.getAttribute('class')||'');
  if(h1){
    fire(h1[2],'mousemove',h1[0],h1[1]);
    out.hoverShown=document.getElementById('tip').style.display;
    out.hoverTitle=(document.querySelector('#tip .c-title')||{}).textContent;
    out.hoverRows=document.querySelectorAll('#tip .c-row').length;
    fire(h1[2],'pointerdown',h1[0],h1[1],PointerEvent);fire(window,'pointerup',h1[0],h1[1],PointerEvent);
    out.cardHidden=document.getElementById('card').hidden;
    out.cardTitle=(document.querySelector('#card .c-title')||{}).textContent;
    out.cardRows=document.querySelectorAll('#card .c-row').length;
  }
  document.body.setAttribute('data-t','done');
  const pre=document.createElement('pre');pre.id='dbg';pre.textContent=JSON.stringify(out);document.body.appendChild(pre);
 }catch(e){document.body.setAttribute('data-t','EXC '+e.message+' '+(e.stack||'').split(NL)[1]);}
},2500);
