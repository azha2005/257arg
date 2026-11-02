'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert');
const D=JSON.parse(fs.readFileSync(path.join(__dirname,'datos.json'),'utf8'));
const E=require('./motor.js');
const close=(a,b,eps=.02)=>assert(Math.abs(a-b)<eps,`${a} != ${b}`);
const census=g=>E.sum(g.votes)+g.abstention;
let cases=0;
for(const local of [true,false])for(let m=0;m<4;m++)for(let r=-1;r<18;r++)for(const [blank,abstain]of [[0,0],[.15,.2],[1,0],[0,1]]) {
 const o={model:m,removed:r,blank,abstain,local},n=E.first(D,o);
 close(E.sum(n.totals),census(D.geographies[0]));
 if(r>=0)close(n.totals[r],0);
 assert(n.totals.every(x=>Number.isFinite(x)&&x>=-1e-5));
 const sums=Array(20).fill(0);
 for(let geo=1;geo<25;geo++) {
  const s=E.first(D,{...o,geo});close(E.sum(s.totals),census(D.geographies[geo]));
  s.totals.forEach((x,i)=>sums[i]+=x);
  const rr=E.runoff(D,{...o,geo,a:n.rank[0],b:n.rank[1],poll:'pre'},s);
  close(E.sum(rr.totals),census(D.geographies[geo]));
 }
 sums.forEach((x,i)=>close(x,n.totals[i]));
 const round=E.runoff(D,{...o,a:n.rank[0],b:n.rank[1],poll:'pre'},n);
 close(E.sum(round.totals),census(D.geographies[0]));cases++;
}
// Cada pareja y cada encuesta, con calibración solo sobre el electorado real.
let calibrated=0;
for(let m=0;m<4;m++)for(let a=0;a<18;a++)for(let b=a+1;b<18;b++) {
 for(const poll of ['pre','may','none',...D.polls.pares.map(p=>p.id)]) {
  const p=E.probabilities(D,m,a,b,poll,true);
  assert(p.p.every(x=>Number.isFinite(x)&&x>=0&&x<=1));
  if(p.poll&&p.reached){close(E.sum(p.p.map((x,i)=>x*D.geographies[0].votes[i]))/D.total_positive,p.target,1e-9);calibrated++;}
 }
}
// La preferencia binaria conservada debe ser invariante ante la reasignación
// de un tercero si no hay salida del voto positivo ni cambio de finalistas.
for(let m=0;m<4;m++) {
 const before=E.runoff(D,{model:m,removed:-1,a:0,b:1,memory:'origin',poll:'pre'});
 const after=E.runoff(D,{model:m,removed:2,a:0,b:1,memory:'origin',poll:'pre'});
 close(before.totals[0],after.totals[0]);close(before.totals[1],after.totals[1]);
}
// Los residuales no publicados de OPSM permanecen sin atribuir en la fuente.
for(const p of D.polls.cruces_por_origen.filter(p=>p.firma==='OPSM'))close(p.K+p.M+p.otra_respuesta+p.indeciso+p.no_publicado,100,1e-9);
assert.throws(()=>E.first(D,{removed:0,blank:.8,abstain:.8}));
assert.throws(()=>E.runoff(D,{a:0,b:0}));
assert.throws(()=>E.first(D,{removed:0,custom:Array(18).fill(0)}));
// Coherencia retirada–balotaje: en cada par con encuesta, los votantes del
// retirado reparten entre esos dos como en el balotaje calibrado. Nacional
// = suma de unidades locales, así que se tolera el desvío de la agregación.
let coherent=0,maxGap=0,maxLS=0;
for(let r=0;r<5;r++)for(let m=0;m<4;m++){
 const t=E.tilt(D,m,r,'fit'),loc=E.first(D,{removed:r,model:m});
 const P=E.preference(D.models[m].joints[0],r,[...Array(18).keys()].filter(i=>i!==r)).map((x,i)=>i<5?x*Math.exp(t.u[i]):x);
 for(const e of t.pairs){
  const ls=Math.abs(P[e.a]/(P[e.a]+P[e.b])-e.q);maxLS=Math.max(maxLS,ls);
  // Con tres pares (un solo vecino común) el ajuste es exacto.
  if(t.pairs.length===3)close(ls,0,1e-9);
  maxGap=Math.max(maxGap,Math.abs(loc.p[e.a]/(loc.p[e.a]+loc.p[e.b])-e.q));coherent++;}
 const old=E.first(D,{removed:r,model:m,coherent:false});
 close(E.sum(loc.p.slice(5)),E.sum(old.p.slice(5)),1e-6);
}
// Con cinco pares el sistema está sobredeterminado (mínimos cuadrados) y la
// suma de unidades locales agrega otro desvío: se acota, no se exige cero.
assert(maxGap<0.13&&maxLS<0.12,'Retirada incoherente con el balotaje: '+maxGap+' / '+maxLS);
console.log(JSON.stringify({escenarios_conservacion:cases,calibraciones_verificadas:calibrated,pares_coherentes:coherent,desvio_max_minimos_cuadrados:maxLS,desvio_max_local:maxGap,estado:'correcto'},null,2));
const rows=[];
for(let r=0;r<18;r++)for(let m=0;m<4;m++) {
 const o={removed:r,model:m},one=E.first(D,o),two=E.runoff(D,{...o,a:one.rank[0],b:one.rank[1]},one);
 rows.push({retirado:D.candidates[r].name,modelo:D.models[m].name,primero:D.candidates[one.rank[0]].short,
  primero_pct:one.totals[one.rank[0]]/one.positive*100,segundo:D.candidates[one.rank[1]].short,
  segundo_pct:one.totals[one.rank[1]]/one.positive*100,gana_primera:one.winsFirst,
  balotaje_a:D.candidates[two.a].short,a_pct:two.share*100,balotaje_b:D.candidates[two.b].short,
  b_pct:(1-two.share)*100,encuesta:two.poll?.id??'sin_encuesta',ajuste_local:true,aviso:'Simulación condicional; afinidad histórica no es segunda preferencia'});
}
const cols=Object.keys(rows[0]);fs.writeFileSync(path.join(__dirname,'escenarios_predeterminados.csv'),'\ufeff'+[cols,...rows.map(r=>cols.map(c=>r[c]))].map(r=>r.map(x=>'"'+String(x).replaceAll('"','""')+'"').join(',')).join('\r\n'));
fs.writeFileSync(path.join(__dirname,'verificacion.json'),JSON.stringify({cases,calibrated,ok:true},null,2));
console.log(JSON.stringify(rows.filter(r=>r.modelo===D.models[0].name).slice(0,5),null,2));
