/* Extensión de escenario: reutiliza el SVG, recuadros y leyenda de mapa2003. */
const AtlasScenario2003=(()=>{
 'use strict';
 const D=ATLAS_INPUT.sim,E=Escenarios2003,N=DATA_UNITS(),nf=new Intl.NumberFormat('es-AR',{maximumFractionDigits:0});
 function DATA_UNITS(){return ATLAS_INPUT.units;}
 const num=x=>nf.format(x),pct=x=>(100*x).toLocaleString('es-AR',{minimumFractionDigits:2,maximumFractionDigits:2})+' %';
 const opts={removed:D.candidates.findIndex(c=>c.id===DEFAULT_REMOVED),model:0,geo:0,blank:0,abstain:0,out:.03,poll:'fit',memory:'destination',local:true,coherent:true};
 let stage=1,focus=1,pair='auto',ds,current;
 const codes=D.candidates.map(c=>c.id),C=Object.fromEntries(D.candidates.map((c,i)=>[c.id,{n:c.short+(i>=5?'*':''),sub:c.id==='M'?'Lealtad':c.id==='K'?'Frente para la Victoria':c.id==='L'?'Recrear':c.id==='R'?'Movimiento Popular':c.id==='C'?'ARI':'Perfil agregado',base:c.color,logo:({M:'PJ',K:'FPV',L:'REC',R:'MNP',C:'ARI',MOREAU:'UCR'})[c.id]||c.short.slice(0,3).toUpperCase()}]));
 C.BN={n:'Blanco y nulo',base:'#888888',logo:'B/N'};C.NV={n:'No votó',base:'#a5a5a5',logo:'NV'};C.OUT={n:'Fuera del voto positivo',base:'#888888',logo:'—'};
 if(ATLAS_INPUT.logos)for(const [k,img]of Object.entries(ATLAS_INPUT.logos)){C[k].img=img;C[k].logo_mode='original';}
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function calc(geo=0,precomputed=null,finalists=null){
  const r1=E.first(D,{...opts,geo}),nat=geo===0?r1:finalists?null:E.first(D,opts);
  let [a,b]=finalists||(pair==='auto'?[nat.rank[0],nat.rank[1]]:pair.split('-').map(Number));
  if(a===opts.removed||b===opts.removed){pair='auto';[a,b]=[nat.rank[0],nat.rank[1]];}
  const r2=E.runoff(D,{...opts,geo,a,b,precomputed},r1);return{r1,r2,a,b};
 }
 function unitCalc(u,a,b,precomputed){
  if(D.local_units){
   const unit=D.local_units.findIndex(q=>q.i===u.i);
   const r1=E.first(D,{...opts,geo:u.geo,unit}),r2=E.runoff(D,{...opts,geo:u.geo,unit,a,b,precomputed},r1);
   const historyNote=!opts.local||stage===0?'':opts.model===3?' El libro 2001 no aporta aquí un margen histórico local compatible; se condiciona su prior nacional al dato local 2003.':D.local_units[unit].historical_1999?'':' Antecedente local 1999 excluido o ausente en el cruce validado; se usa un prior nacional, sin presentarlo como observado.';
   return{r1,r2,a,b,historyNote};
  }
  const proxy={...D,geographies:[D.geographies[0],{...u,abstention:u.abstention??0}],models:D.models.map(m=>({...m,joints:[m.joints[0],m.joints[u.geo]]}))};
  const r1=E.first(proxy,{...opts,geo:1}),r2=E.runoff(proxy,{...opts,geo:1,a,b,precomputed},r1);return{r1,r2,a,b};
 }
 function record(cal,base){
  const {r1,r2}=cal,v=stage===0?base.votes:stage===1?r1.totals:r2.totals;
  let positive,lines,rank,metrics;
  if(stage<2){
   positive=stage===0?E.sum(base.votes.slice(0,18)):r1.positive;
   rank=Array.from({length:18},(_,i)=>i).filter(i=>stage===0||i!==opts.removed).sort((a,b)=>v[b]-v[a]);
   lines=rank.filter(i=>v[i]>.001).map(i=>[codes[i],v[i],v[i]/positive*100]);
   const blank=stage===0?base.votes[18]:r1.totals[18],nv=stage===0?base.abstention:r1.totals[19];
   lines.push(['BN',blank,null],['NV',nv,null]);
   metrics=[['Votos positivos esperados',num(positive)],['Blanco y nulo',num(blank)],['No votó',base.abstention===null?'No verificable':num(nv)]];
   const w=rank[0],runner=rank[1];
   if(base.abstention===null)lines=lines.filter(l=>l[0]!=='NV');
   return {w:codes[w],q:v[w]/positive*100,lines,metrics,note:(stage===0?'Base presidencial PolAr calibrada a la tabla nacional; no es el definitivo local.':'Retirada contrafáctica; reparto por afinidades históricas, no segundas preferencias observadas.')+(base.abstention===null?' Abstención no verificable: en PolAr los emitidos superan al padrón en 236. No se imputó.':'')+(cal.historyNote||''),positive,margin:(v[w]-v[runner])/positive*100,values:v};
  }
  positive=r2.valid;rank=[0,1].sort((a,b)=>v[b]-v[a]);
  lines=rank.map(i=>[codes[i===0?r2.a:r2.b],v[i],v[i]/positive*100]);lines.push(['OUT',v[2],null]);
  metrics=[['Votos positivos esperados',num(positive)],[base.abstention===null?'Fuera del positivo (mínimo conocido)':'Fuera del voto positivo',num(v[2])]];
  return {w:lines[0][0],q:lines[0][2],lines,metrics,note:'Segunda vuelta simulada; fuera del positivo incluye abstenciones, blanco/nulo y la exclusión supuesta. No hay participación identificada.'+(base.abstention===null?' Abstención real local desconocida y excluida de ese conteo.':'')+(cal.historyNote||''),positive,margin:Math.abs(v[0]-v[1])/positive*100,values:v};
 }
 function lighten(hex,k){const c=[1,3,5].map(i=>parseInt(hex.substr(i,2),16));return '#'+c.map(x=>Math.round(255*(1-k)+x*k).toString(16).padStart(2,'0')).join('');}
 const marginStops=[['#fff7ec','0–5'],['#fee8c8','5–10'],['#fdbb84','10–20'],['#e34a33','20–40'],['#7f0000','40+']];
 function refresh(){
  const nat=calc(),national=record(nat,D.geographies[0]);
  const precomputed={p:nat.r2.p,poll:nat.r2.poll,target:nat.r2.target,reached:nat.r2.reached,fixed:nat.r2.fixed};
  const province={};D.geographies.slice(1).forEach((g,j)=>province[g.name]=record(calc(j+1,precomputed,[nat.a,nat.b]),g));
  const units=N.map(u=>u.missing?{fill:u.malvinas?'#a9a9a9':'#e6dcc3',note:u.malvinas?'Sin voto registrado para esta unidad.':u.reason||'Pendiente: sin dato territorial emparejado.',lines:[],metrics:[]}:record(unitCalc(u,nat.a,nat.b,precomputed),u));
  const winners=new Set(units.filter(u=>u.w).map(u=>u.w));
  const totals=stage<2?D.candidates.map((c,i)=>[c.id,stage===0?D.geographies[0].votes[i]:nat.r1.totals[i]]):[[codes[nat.a],nat.r2.totals[0]],[codes[nat.b],nat.r2.totals[1]]];
  const cands=totals.filter(([c,v])=>winners.has(c)&&v>0).sort((a,b)=>b[1]-a[1]).map(([code,votes])=>({code,votes,pct:votes/national.positive*100}));
  const others=E.sum(totals.filter(([c])=>!winners.has(c)).map(x=>x[1]));
  const slices=cands.map(c=>({code:c.code,v:c.votes}));if(others>0)slices.push({fill:'#717274',v:others});
  const partp=stage<2?(stage===0?E.sum(D.geographies[0].votes):E.sum(nat.r1.totals.slice(0,19)))/D.registered*100:null;
  const topline={cands,slices,partp,metrics:national.metrics};
  const note='Simulación condicional. Base: presidenciales 2003 (PolAr / tabla nacional). '+D.models[opts.model].name+'. '+(nat.r2.poll?`Balotaje: ${nat.r2.poll.firma}, ${nat.r2.poll.fecha}.`:'Sin encuesta numérica localizada para el cruce; balotaje por afinidad.')+' Malvinas en gris; datos ausentes en beige.';
  const keylegend={keys:[['#e6dcc3','Pendiente'],['#a9a9a9','Sin voto registrado']]};
  const modes=[{id:'gan',tile:'GANÓ',note,units,prov:province,national:topline,legend:keylegend}];
  const fc=codes[focus],basecolor=C[fc].base,focusRecord=r=>{
   if(!r.w)return {...r};const line=r.lines.find(l=>l[0]===fc),value=line?line[2]||0:0;
   return {...r,fill:lighten(basecolor,Math.min(1,.12+value/100*.88)),note:r.note+' Coropleta de '+C[fc].n+'.'};
  };
  modes.push({id:'voto',tile:'VOTOS',note,units:units.map(focusRecord),prov:Object.fromEntries(Object.entries(province).map(([p,r])=>[p,focusRecord(r)])),national:topline,legend:{title:C[fc].n+' · votos positivos (%)',bars:false,stops:[0,20,40,60,80,100].map(q=>[lighten(basecolor,.12+q/100*.88),String(q)])}});
  const marginRecord=r=>!r.w?{...r}:{...r,fill:marginStops[r.margin>=40?4:r.margin>=20?3:r.margin>=10?2:r.margin>=5?1:0][0]};
  modes.push({id:'margen',tile:'MARGEN',note,units:units.map(marginRecord),prov:Object.fromEntries(Object.entries(province).map(([p,r])=>[p,marginRecord(r)])),national:topline,legend:{title:'Ventaja sobre el segundo (puntos)',bars:false,stops:marginStops}});
  modes.forEach((m,i)=>Object.assign(ds.modes[i],m));
  const retired=opts.removed>=0?'Sin '+D.candidates[opts.removed].short:'Sin retirada';
  ds.sets['1'].subtitle=retired+' · '+(stage===0?'Referencia':stage===1?'1.ª vuelta':'2.ª vuelta');
  ds.slug='escenario_2003_'+(opts.removed>=0?codes[opts.removed].toLowerCase():'base')+'_'+(stage===2?'balotaje':'primera');
  current={nat,units,province,topline};
  return current;
 }
 function initial(){
  ds={year:2003,slug:'escenario_2003',locale:'es-AR',country:'Argentina',title:'Simulación presidencial de Argentina de',exterior:false,sets:{'1':{label:'Escenario',subtitle:''}},labels:{results:'Resultados simulados',won:'GANÓ',pie1:'Proporción sobre votos positivos',pie2:'Anillo: participación simulada',provinces:'Provincias'},candidates:C,insets:ATLAS_INPUT.insets,solid:[],territories:ATLAS_INPUT.territories,modes:[{id:'gan'},{id:'voto'},{id:'margen'}]};
  refresh();return ds;
 }
 const el=id=>document.getElementById(id),op=(v,t)=>`<option value="${esc(v)}">${esc(t)}</option>`;
 function update(){
  try{
   opts.removed=Number(el('s-retired').value);opts.model=Number(el('s-model').value);stage=Number(el('s-stage').value);focus=Number(el('s-focus').value);opts.poll=el('s-poll').value;pair=el('s-pair').value;opts.local=el('s-local').value==='local';opts.coherent=el('s-coherent').value==='on';
   opts.blank=Number(el('s-blank').value)/100;opts.abstain=Number(el('s-abstain').value)/100;opts.out=Number(el('s-out').value)/100;opts.memory=el('s-memory').value;
   if(opts.blank+opts.abstain>1||opts.out>=1||opts.out<0||opts.blank<0||opts.abstain<0)throw Error('Los porcentajes de salida de primera vuelta deben sumar hasta 100; la exclusión de segunda debe ser menor que 100.');
   refresh();el('s-pair').value=pair;
   window.__atlas.setMode(window.__atlas.mode);
   const subtitle=el('sub');subtitle.setAttribute('x','1886');subtitle.setAttribute('text-anchor','end');subtitle.setAttribute('font-size','24');subtitle.removeAttribute('textLength');
   if(subtitle.getComputedTextLength()>380){subtitle.setAttribute('textLength','380');subtitle.setAttribute('lengthAdjust','spacingAndGlyphs');}
   el('pie2').textContent=stage<2?'Anillo: participación simulada':'Sin estimación de participación';
   const n=current.nat,firstwinner=n.r1.rank[0],poll=n.r2.poll;
   el('scenario-status').textContent=(stage===0?'Referencia territorial calibrada. ':'Simulación, no resultado observado. ')+(opts.removed>=5?'Candidatura menor: afinidad individual no identificada. ':'')+`Primera vuelta nacional: ${D.candidates[firstwinner].short} ${pct(n.r1.totals[firstwinner]/n.r1.positive)}. `+(n.r1.winsFirst?'Supera el umbral para ganar en primera vuelta; el balotaje es exploratorio. ':`Cruce: ${D.candidates[n.a].short} – ${D.candidates[n.b].short}. `)+(stage===2?(poll?`Encuesta: ${poll.firma}, ${poll.fecha}. `:'Sin encuesta numérica localizada; resultado por afinidad. '):'')+`Modelo: ${D.models[opts.model].name}. Ver métodos y sensibilidad en el simulador.`;
   let source=el('scenario-svg-source');if(!source){source=document.createElementNS('http://www.w3.org/2000/svg','g');source.id='scenario-svg-source';el('atlas').appendChild(source);}source.replaceChildren();
   ['Modelo: '+D.models[opts.model].name,'Base: presidenciales 2003 · PolAr / Wikipedia.',opts.local?'Afinidad ajustada localmente; no voto individual.':'Reparto provincial uniforme (comparación).','*Menores: afinidad agregada, no identificada.',stage===2&&poll?'Encuesta: '+poll.firma.split(' (')[0]+', '+poll.fecha:'Fuentes y supuestos completos en el HTML.'].forEach((line,i)=>{const t=document.createElementNS('http://www.w3.org/2000/svg','text');t.setAttribute('x','85');t.setAttribute('y',1530+i*20);t.setAttribute('font-size','13');t.setAttribute('fill','#616161');t.textContent=line;source.appendChild(t);});
   window.__scenario={opts:{...opts},stage,focus,pair,units:current.units,national:current.topline,first:n.r1,second:n.r2};
  }catch(error){el('scenario-status').textContent=error.message;el('scenario-status').setAttribute('role','alert');}
 }
 function attach(){
  const holder=el('scenario-controls');
  if(document.body.dataset.bg==='white')el('b-bg').textContent='Fondo: blanco';
  const pairs=[op('auto','Dos primeros nacionales')];for(let a=0;a<5;a++)for(let b=a+1;b<5;b++)pairs.push(op(a+'-'+b,D.candidates[a].short+' / '+D.candidates[b].short));
  holder.innerHTML=`<label>Se retira<select id="s-retired">${op(-1,'Nadie (referencia)')}${D.candidates.map((c,i)=>op(i,c.name)).join('')}</select></label><label>Modelo<select id="s-model">${D.models.map((m,i)=>op(i,m.name)).join('')}</select></label><label>Distribución territorial<select id="s-local">${op('local','Ajuste local (predeterminado)')}${op('province','Provincial uniforme: comparación')}</select></label><label>Reparto del retirado<select id="s-coherent">${op('on','Coherente con balotajes encuestados')}${op('off','Solo afinidad por origen')}</select></label><label>Vuelta<select id="s-stage">${op(0,'Base real calibrada')}${op(1,'Primera vuelta simulada')}${op(2,'Segunda vuelta simulada')}</select></label><label>Coropleta de votos<select id="s-focus">${D.candidates.map((c,i)=>op(i,c.short)).join('')}</select></label><label>Encuestas<select id="s-poll">${op('fit','Ajuste conjunto antes del 27/4')}${op('pre','Última por par antes del 27/4')}${op('may','Incluir OPSM de mayo (M/K)')}${op('none','Sin encuesta: afinidad')}</select></label><label>Balotaje<select id="s-pair">${pairs.join('')}</select></label><details><summary>Supuestos de transferencia</summary><label>A blanco/nulo (%)<input id="s-blank" type="number" min="0" max="100" value="0"></label><label>A abstención (%)<input id="s-abstain" type="number" min="0" max="100" value="0"></label><label>Exclusión del positivo en balotaje (%)<input id="s-out" type="number" min="0" max="99" value="3"></label><label>Voto redistribuido<select id="s-memory">${op('destination','Se comporta como su nuevo destino')}${op('origin','Conserva el voto real de origen')}</select></label></details><a href="../../analisis/escenarios2003/simulador_2003.html" target="_blank">Encuestas, Sankey y sensibilidad</a><span id="scenario-status" aria-live="polite"></span>`;
  el('s-retired').value=opts.removed;el('s-model').value=opts.model;el('s-stage').value=stage;el('s-focus').value=focus;
  holder.addEventListener('change',update);update();
 }
 return {initial,attach,refresh};
})();
