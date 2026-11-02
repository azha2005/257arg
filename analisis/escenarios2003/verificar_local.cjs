const fs=require('fs'),path=require('path'),assert=require('assert'),E=require('./motor.js');
const D=JSON.parse(fs.readFileSync(path.join(__dirname,'datos.json'),'utf8'));
const rows=[];
for(let r=0;r<5;r++)for(let geo=1;geo<25;geo++){
 const indices=D.local_units.map((u,i)=>[u,i]).filter(([u])=>u.geo===geo&&u.votes[r]>0);
 if(indices.length<2)continue;
 const transfer=indices.map(([u,i])=>({w:u.votes[r],p:E.first(D,{removed:r,model:0,geo,unit:i}).p}));
 const total=E.sum(transfer.map(x=>x.w)),mean=Array.from({length:18},(_,j)=>E.sum(transfer.map(x=>x.w*x.p[j]))/total);
 const std=mean.map((m,j)=>Math.sqrt(E.sum(transfer.map(x=>x.w*(x.p[j]-m)**2))/total)*100);
 rows.push({retirado:D.candidates[r].short,provincia:D.geographies[geo].name,unidades:indices.length,
  desvio_medio_reparto_pp:E.sum(std.filter((_,j)=>j!==r))/17,max_desvio_destino_pp:Math.max(...std)});
}
assert(rows.filter(r=>r.max_desvio_destino_pp>1).length>100,'Persisten repartos territoriales casi constantes');
// Todos los votos por candidato de cada matriz local deben conservar su base.
let error=0;
for(const m of D.models)for(let u=0;u<D.local_units.length;u++)for(let j=0;j<19;j++){
 const z=E.sum(m.local_joints[u].map(r=>r[j]));error=Math.max(error,Math.abs(z-D.local_units[u].votes[j]));
}
assert(error<.001);
const report={comparaciones:rows.length,con_heterogeneidad_mayor_1pp:rows.filter(r=>r.max_desvio_destino_pp>1).length,max_error_margen_local:error,
 warning:'Heterogeneidad condicionada a datos locales; no valida segundas preferencias contrafácticas.',rows};
fs.writeFileSync(path.join(__dirname,'heterogeneidad_local.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,rows:report.rows.filter(r=>r.provincia==='Chaco')}));
