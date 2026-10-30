/* Leyenda de las legislativas 2003-2025 (incluidas 2009/2013): filas de «Resultados» y degradado de tonos.
   Reemplaza shade() de la plantilla: los amarillos se oscurecen hacia el ámbar en vez de hacia el oliva. */
const hsl=h=>{const[r,g,b]=hex2(h).map(v=>v/255),mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2;let H=0,S=0;
  if(mx!==mn){const d=mx-mn;S=l>.5?d/(2-mx-mn):d/(mx+mn);H=mx===r?(g-b)/d+(g<b?6:0):mx===g?(b-r)/d+2:(r-g)/d+4;H*=60;}return[H,S,l]};
const fromhsl=(H,S,L)=>{H=(H+360)%360;const a=S*Math.min(L,1-L),f=n=>{const k=(n+H/30)%12;return L-a*Math.max(-1,Math.min(k-3,9-k,1))};return rgb(f(0)*255,f(8)*255,f(4)*255)};
const warm=h=>{const[H,S]=hsl(h);return H>38&&H<68&&S>.5};
const lumi=h=>{const c=hex2(h);return .2126*c[0]+.7152*c[1]+.0722*c[2]};
const ink=h=>{const[H,S,L]=hsl(h);return fromhsl(warm(h)?H-12:H,Math.min(S,.85),Math.min(L,warm(h)?.32:.36))};
const shade=(code,i)=>{const b=CAND[code].base;if(i===0)return mixw(b,.15);const k=SHADE_K[i];
  if(!warm(b))return mulc(b,k);const[H,S,L]=hsl(b);return fromhsl(H-(1-k)*24,S,L*(.3+.7*k))};
/* Barra maciza como en los demás atlas, pero con el color del partido sin oscurecer (antes se multiplicaba
   por .66 y quedaba apagada). Texto blanco, o gris oscuro si el color es claro. Los logos van transparentes
   sobre la barra, como en los demás atlas (pedido del usuario: sin pastilla blanca ni cambio de color de barra). */
/* Tratamiento de cada logo en la leyenda: "blanco" = silueta blanca (logos de color sin fondo); "tinta" = la tinta
   oscura pasa a blanco y el fondo claro se vuelve transparente (logos de letras oscuras). Sin entrada: logo original. */
/* Los partidos con bloque de un mapa presidencial de la Wikipedia (bloques_wiki.py: FPV, Cambiemos, JxC, FdT, UP,
   LLA, UNA, CF, Hacemos, ARI, CC, FAP, UDESO, FP...) no pasan por esta tabla. */
const LOGO_ESTILO=[
  ["unidad ciudadana","blanco"],["fuerza patria","blanco"],["juntos somos río negro","blanco"],["unión por córdoba","blanco"],
  ["innovación federal","tinta"],["renovador de salta","tinta"],["acuerdo cívico","tinta"],
  ["dignidad y la independencia","tinta"],["compromiso para el cambio","tinta"],["nuevo encuentro","tinta"],
  ["unión de los neuquinos","tinta"]];
const logoMode=n=>{n=(n||"").toLowerCase();const e=LOGO_ESTILO.find(([k])=>n.includes(k));return e?e[1]:null};
const soft=h=>{const[H,S,L]=hsl(h);return fromhsl(H,Math.min(S,.82),Math.max(Math.min(L,.6),.3))};
function LEGEND_ROW(g,C,c,y,rows,win,hh,s){   // s: escala de letras y logos (por defecto 1; leyendas cortas con barras altas)
  s=s||1;
  const h=hh||(rows.length>12?23:27),bar=soft(C.base),tc=lumi(bar)>165?"#2b2b2b":"#fff";
  el("rect",{x:80,y,width:5,height:h-1,fill:mixw(bar,.42)},g);
  el("rect",{x:93,y,width:win?431:337,height:h,fill:bar},g);
  if(C.img&&C.blk){   // bloque de un mapa presidencial de la Wikipedia, alineado a la izquierda
    const cv=el("svg",{x:93,y,width:92*s,height:h,overflow:"hidden"},g);
    const bh=Math.min(h*1.15,92*s/(C.ar||1)),bw=bh*(C.ar||1);   // leve zoom: recorta apenas arriba y abajo
    el("image",{href:C.img,x:0,y:(h-bh)/2,width:bw,height:bh,preserveAspectRatio:"xMinYMid meet"},cv);
  }else if(C.img){
    // Como los mapas presidenciales de la Wikipedia (TODOS blanco en 2019, sol de UP en 2023): la barra no cambia;
    // el logo que no contrasta con ella va en blanco. Elegido a mano, partido por partido (LOGO_ESTILO).
    const md=logoMode(C.n),filt=md?"lg_"+md:null;
    if(filt&&!document.getElementById(filt)){const f=el("filter",{id:filt,"color-interpolation-filters":"sRGB"},g.ownerSVGElement||g);
      el("feColorMatrix",{type:"matrix",values:md==="blanco"?"0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 0"
        :"0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 -0.32 -1.07 -0.11 1.5 0"},f);}   // tinta: lo oscuro pasa a blanco, lo claro a transparente
    const ih=s>1?Math.min(h*(C.bl||1.05),(92*s-6)/(C.ar||1)):h*(C.bl||1.05),iw=ih*(C.ar||1),   /* con barras altas, el logo ancho no pasa del marco */ cv=el("svg",{x:93,y,width:92*s,height:h,overflow:"hidden"},g);   // leve zoom recortado, como antes
    el("image",{href:C.img,x:4,y:(h-ih)/2,width:iw,height:ih,preserveAspectRatio:"xMidYMid meet",...(filt?{filter:`url(#${filt})`}:{})},cv);
  }else{const lg=C.logo||c.code;
    el("text",{x:97,y:y+h/2+6*s,"font-size":(lg.length>3?16:18)*s,fill:tc,"letter-spacing":-0.5},g,lg);
    el("rect",{x:97,y:y+h/2+9*s,width:lg.length*10.5*s,height:2*s,fill:tc,opacity:.8},g);}
  const av=424-(97+92*s)-4,fn=s===1?14.5:Math.min(14.5*s,Math.max(14.5,av/(C.n.length*0.52))),sq=s===1?C.n.length>29:C.n.length*fn*0.52>av;   // nombre largo: primero letra mas chica (no menos que la original), despues se comprime
  el("text",{x:424,y:y+(C.sub?h/2-0.5*s:h/2+5*s),"font-size":fn,fill:tc,"text-anchor":"end",...(sq?{textLength:s===1?232:av,lengthAdjust:"spacingAndGlyphs"}:{})},g,C.n);
  if(C.sub)el("text",{x:424,y:y+h/2+9.5*s,"font-size":10.5*s,fill:tc,"text-anchor":"end",opacity:.9},g,C.sub);
  if(win){
    const wb=mulc(bar,.9),wc=lumi(wb)>165?"#2b2b2b":"#fff";
    el("rect",{x:429,y,width:95,height:h,fill:wb},g);
    el("text",{x:516,y:y+h/2+3*s,"font-size":18.5*s,fill:wc,"text-anchor":"end"},g,f2(c.pct)+"%");
    el("text",{x:516,y:y+h-2.5*s,"font-size":8.5*s,fill:wc,"font-style":"italic","text-anchor":"end",opacity:.85},g,LAB.won);
  }else el("text",{x:516,y:y+h/2+5.5*s,"font-size":16.5*s,fill:ink(C.base),"text-anchor":"end"},g,f2(c.pct)+"%");   // porcentajes encolumnados a la derecha
}
/* Tamano de la leyenda segun la cantidad de filas (pedido del usuario, 30-oct-2026): con pocas filas, barras del alto de
   las de los mapas de la Wikipedia (48 px en este poster); las largas (mas de 12) quedan compactas como antes (big).
   h: alto de barra; s: escala de letras y logos; rh: alto de la franja de tonos; ra: avance de la franja; ts: escala de titulos. */
const LEG_SZ=(n,big)=>{const t=n===0?{h:27,s:1,rh:5.5,ra:8.5}:n<=6?{h:48,s:1.4,rh:9,ra:12}:n<=8?{h:42,s:1.25,rh:8,ra:11}:
  n<=10?{h:36,s:1.12,rh:7,ra:10}:n<=12?{h:30,s:1,rh:6,ra:9}:Object.assign({h:23,s:1,rh:5.5,ra:7},big||{});t.ts=Math.min(t.s,1.25);return t};
/* El cuadro de resultados se ancla por arriba (pedido del usuario): el título «Resultados» queda a la misma altura en
   todos los atlas (la del más largo, 15 filas) y lo que varía es dónde termina. */
const ANCHOR_LEGEND=g=>{g.removeAttribute("transform");const b=g.getBBox();if(b.height)g.setAttribute("transform",`translate(0,${(993-b.y).toFixed(1)})`)};
