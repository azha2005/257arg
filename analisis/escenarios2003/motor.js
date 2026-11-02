/* Motor compartido por el simulador y sus controles. Sin dependencias. */
(function (root) {
  'use strict';
  const sum = a => a.reduce((s,x)=>s+x,0);
  const clamp = (x,a,b) => Math.max(a,Math.min(b,x));
  const logistic = x => 1/(1+Math.exp(-x));
  const logit = x => Math.log(clamp(x,1e-8,1-1e-8)/(1-clamp(x,1e-8,1-1e-8)));
  function preference(J, i, allowed) {
    const p = Array(18).fill(0), source = sum(J.map(r=>r[i]));
    if (!(source>0)) throw Error('Origen sin soporte');
    for (const row of J) {
      const den = sum(allowed.map(j=>row[j]));
      if (den>0) for (const j of allowed) p[j] += row[i]/source*row[j]/den;
    }
    const z=sum(p);
    if (!(z>0)) throw Error('Destinos sin soporte');
    return p.map(x=>x/z);
  }
  // Coherencia retirada–balotaje: la afinidad por origen sola manda, p. ej.,
  // a la mitad del voto de Kirchner a Menem, aunque en el balotaje calibrado
  // esos mismos votantes prefieren a cualquiera antes que a Menem. Se aplica
  // un modelo de Luce: P(j|r) ∝ afinidad(j|r)·exp(u_j), con u ajustado por
  // mínimos cuadrados para que los pares con encuesta reproduzcan la
  // preferencia de los votantes de r en ese balotaje. Solo entre los cinco
  // principales; la masa total de los cinco y la de los menores no cambia.
  const MAJORS=5, tilts=new WeakMap();
  function tilt(data,mi,removed,selection) {
    const u=Array(18).fill(0);
    if(removed<0||removed>=MAJORS||selection==='none') return {u,pairs:[]};
    let cache=tilts.get(data); if(!cache){cache=new Map();tilts.set(data,cache);}
    const key=mi+'|'+removed+'|'+selection; if(cache.has(key)) return cache.get(key);
    const S=Array.from({length:MAJORS},(_,i)=>i).filter(i=>i!==removed);
    const allowed=Array.from({length:18},(_,i)=>i).filter(i=>i!==removed);
    const p0=preference(data.models[mi].joints[0],removed,allowed), pairs=[];
    for(let x=0;x<S.length;x++)for(let y=x+1;y<S.length;y++) {
      const a=S[x],b=S[y],pr=probabilities(data,mi,a,b,selection,false);
      if(!pr.poll||!(p0[a]>0&&p0[b]>0)) continue;
      const q=pr.p[removed];
      pairs.push({a,b,q,poll:pr.poll.id,y:logit(q)-Math.log(p0[a]/p0[b])});
    }
    for(let it=0;it<2000;it++) for(const i of S) {
      let s=0,n=0;
      for(const e of pairs){if(e.a===i){s+=u[e.b]+e.y;n++;}else if(e.b===i){s+=u[e.a]-e.y;n++;}}
      if(n) u[i]=s/n;
    }
    const mass=sum(S.map(i=>p0[i])), tilted=sum(S.map(i=>p0[i]*Math.exp(u[i])));
    if(mass>0&&tilted>0) for(const i of S) u[i]+=Math.log(mass/tilted);
    const out={u,pairs}; cache.set(key,out); return out;
  }
  function applyTilt(p,u) {
    const before=sum(p.slice(0,MAJORS)), t=p.map((x,i)=>i<MAJORS?x*Math.exp(u[i]):x);
    const after=sum(t.slice(0,MAJORS));
    // Conserva exactamente la masa local de los cinco principales.
    return after>0?t.map((x,i)=>i<MAJORS?x*before/after:x):p;
  }
  function first(data, opts={}) {
    const gi=opts.geo??0, mi=opts.model??0, ui=opts.unit;
    const g=ui!=null?data.local_units[ui]:data.geographies[gi];
    const removed=opts.removed??-1, blank=opts.blank??0, abstain=opts.abstain??0;
    if (removed < -1 || removed>=18 || blank<0 || abstain<0 || blank+abstain>1+1e-12) throw Error('Retirada o porcentajes inválidos');
    const allowed=Array.from({length:18},(_,i)=>i).filter(i=>i!==removed);
    if(data.local_units && opts.local!==false && ui==null) {
      const flows=Array.from({length:18},()=>Array(20).fill(0));
      for(let k=0;k<data.local_units.length;k++) {
        if(gi && data.local_units[k].geo!==gi)continue;
        const sub=first(data,{...opts,unit:k});
        for(let i=0;i<18;i++)for(let j=0;j<20;j++)flows[i][j]+=sub.flows[i][j];
      }
      const totals=Array.from({length:20},(_,j)=>sum(flows.map(r=>r[j])));
      totals[18]+=g.votes[18];totals[19]+=g.abstention;
      const positive=sum(totals.slice(0,18)),rank=allowed.slice().sort((a,b)=>totals[b]-totals[a]);
      const share=totals[rank[0]]/positive,gap=(totals[rank[0]]-totals[rank[1]])/positive;
      const p=removed>=0&&1-blank-abstain>1e-12?flows[removed].slice(0,18).map(x=>x/(g.votes[removed]*(1-blank-abstain))):Array(18).fill(0);
      return {totals,flows,positive,rank,winsFirst:share>.45||(share>=.40&&gap>.10),p};
    }
    const joint=ui!=null&&opts.local!==false?data.models[mi].local_joints[ui]:data.models[mi].joints[gi];
    let p=removed>=0?preference(g.votes[removed]>0?joint:data.models[mi].joints[0],removed,allowed):Array(18).fill(0);
    if (removed>=0 && opts.coherent!==false && !opts.custom) p=applyTilt(p,tilt(data,mi,removed,opts.poll??'fit').u);
    if (opts.custom) {
      if(opts.custom.length!==18 || opts.custom.some(x=>!Number.isFinite(x)||x<0)) throw Error('Reparto inválido');
      p=opts.custom.map((x,i)=>i===removed?0:x);
      if (sum(p)<=0) throw Error('El reparto necesita al menos un destino');
      p=p.map(x=>x/sum(opts.custom.filter((_,i)=>i!==removed)));
    }
    const flows=Array.from({length:18},()=>Array(20).fill(0));
    for(let i=0;i<18;i++) {
      const v=g.votes[i];
      if(i!==removed) flows[i][i]=v;
      else {
        for(const j of allowed) flows[i][j]=v*(1-blank-abstain)*p[j];
        flows[i][18]=v*blank; flows[i][19]=v*abstain;
      }
    }
    let totals=Array.from({length:20},(_,j)=>sum(flows.map(r=>r[j])));
    totals[18]+=g.votes[18]; totals[19]+=g.abstention??0;
    if(gi===0 && data.geographies.length>1 && ui==null) {
      // El total nacional ES la suma de los escenarios provinciales.
      // No se aplica una matriz nacional distinta después de agregarlos.
      for(const row of flows) row.fill(0);
      totals=Array(20).fill(0);
      for(let k=1;k<data.geographies.length;k++) {
        const sub=first(data,{...opts,geo:k});
        for(let j=0;j<20;j++) {
          totals[j]+=sub.totals[j];
          for(let i=0;i<18;i++) flows[i][j]+=sub.flows[i][j];
        }
      }
      if(removed>=0 && 1-blank-abstain>1e-12) p=flows[removed].slice(0,18).map(x=>x/(g.votes[removed]*(1-blank-abstain)));
    }
    const positive=sum(totals.slice(0,18));
    const rank=allowed.slice().sort((a,b)=>totals[b]-totals[a]);
    const share=totals[rank[0]]/positive, gap=(totals[rank[0]]-totals[rank[1]])/positive;
    const winsFirst=share>0.45 || (share>=0.40 && gap>0.10);
    return {totals,flows,positive,rank,winsFirst,p};
  }
  function findPoll(data,a,b,selection='pre') {
    const ids=data.candidates.map(c=>c.id), ka=ids[a],kb=ids[b];
    const pair=p=>(p.a===ka&&p.b===kb)||(p.a===kb&&p.b===ka);
    let found=data.polls.pares.filter(pair);
    if(selection==='none') return null;
    if(selection==='pre') found=found.filter(p=>p.fecha<'2003-04-27');
    else if(selection==='may') found=found.filter(p=>p.id==='opsm_may11_km'||p.fecha<'2003-04-27');
    else found=found.filter(p=>p.id===selection);
    return found.sort((a,b)=>a.fecha.localeCompare(b.fecha)).at(-1)??null;
  }
  // Ajuste conjunto: un atractivo β por candidato principal (Menem = 0) para
  // todas las encuestas anteriores al 27/4 a la vez, ponderadas por muestra.
  // En el par (a,b) los votantes de i eligen a con σ(logit(afinidad)+β_a−β_b).
  // Reemplaza «la última cifra de cada par» y da un valor también para los
  // pares sin encuesta. La afinidad por origen sigue fijando las diferencias
  // entre electorados; las encuestas, el nivel de cada candidato.
  const fits=new WeakMap();
  function baseRow(J,a,b){return Array.from({length:18},(_,i)=>i===a?0.98:i===b?0.02:preference(J,i,[a,b])[a]);}
  function jointFit(data,mi) {
    let cache=fits.get(data); if(!cache){cache=new Map();fits.set(data,cache);}
    if(cache.has(mi)) return cache.get(mi);
    const ids=data.candidates.map(c=>c.id), J=data.models[mi].joints[0], n=data.geographies[0].votes, N=sum(n.slice(0,18));
    const obs=data.polls.pares.filter(p=>p.fecha<'2003-04-27').map(p=>{
      const a=ids.indexOf(p.a),b=ids.indexOf(p.b);
      return {a,b,t:p.a_pct/(p.a_pct+p.b_pct),w:p.n||1000,base:baseRow(J,a,b).map(logit),id:p.id};
    }).filter(o=>o.a>=0&&o.a<MAJORS&&o.b>=0&&o.b<MAJORS);
    const pred=(o,beta)=>sum(o.base.map((x,i)=>n[i]*logistic(x+beta[o.a]-beta[o.b])))/N;
    const loss=beta=>sum(obs.map(o=>o.w*(pred(o,beta)-o.t)**2));
    const beta=Array(MAJORS).fill(0); let step=1;
    // Búsqueda por coordenadas: suficiente para cuatro parámetros.
    while(step>1e-7) {
      let moved=false;
      for(let j=1;j<MAJORS;j++) for(const s of [step,-step]) {
        const tr=beta.slice(); tr[j]+=s;
        if(loss(tr)<loss(beta)-1e-15){beta.splice(0,MAJORS,...tr);moved=true;}
      }
      if(!moved) step/=2;
    }
    const residuals=obs.map(o=>({id:o.id,observado:o.t,ajustado:pred(o,beta)}));
    const out={beta,residuals,n:obs.length}; cache.set(mi,out); return out;
  }
  function probabilities(data,mi,a,b,selection='fit',cross=false) {
    if(a===b||a<0||b<0||a>=18||b>=18) throw Error('Finalistas inválidos');
    const J=data.models[mi].joints[0], n=data.geographies[0].votes;
    if(selection==='fit' && a<MAJORS && b<MAJORS) {
      const f=jointFit(data,mi), base=baseRow(J,a,b);
      const p=base.map(x=>logistic(logit(x)+f.beta[a]-f.beta[b]));
      const direct=data.polls.pares.filter(q=>q.fecha<'2003-04-27'&&((q.a===data.candidates[a].id&&q.b===data.candidates[b].id)||(q.a===data.candidates[b].id&&q.b===data.candidates[a].id)));
      const poll={id:'ajuste_conjunto',firma:`Ajuste conjunto de ${f.n} mediciones (${direct.length} de este par)`,fecha:'2003-04-26',url:'encuestas.json',direct:direct.length};
      return {p,poll,target:sum(p.map((x,i)=>x*n[i]))/sum(n.slice(0,18)),reached:true,fixed:[]};
    }
    if(selection==='fit') selection='pre';
    let p=baseRow(J,a,b);
    const poll=findPoll(data,a,b,selection), fixed=new Set();
    let target=null, reached=true;
    if(poll) {
      target=(poll.a===data.candidates[a].id?poll.a_pct:poll.b_pct)/(poll.a_pct+poll.b_pct);
      // OPSM aporta tres filas. Se usan SOLO las respuestas por A o B;
      // la proporción excluida/indecisa no se atribuye a ningún candidato.
      if(cross && poll.id==='opsm_may11_km') {
        for(const row of data.polls.cruces_por_origen.filter(r=>r.firma==='OPSM')) {
          const i=data.candidates.findIndex(c=>c.id===row.origen);
          const aa=row[data.candidates[a].id], bb=row[data.candidates[b].id];
          p[i]=aa/(aa+bb); fixed.add(i);
        }
      }
      const desired=target*sum(n.slice(0,18));
      const evalAt=d=>sum(p.map((x,i)=>n[i]*(fixed.has(i)?x:logistic(logit(x)+d))));
      reached=desired>=evalAt(-40)-1 && desired<=evalAt(40)+1;
      if(reached) {
        let lo=-40,hi=40;
        for(let k=0;k<90;k++) {const mid=(lo+hi)/2;if(evalAt(mid)<desired)lo=mid;else hi=mid;}
        p=p.map((x,i)=>fixed.has(i)?x:logistic(logit(x)+(lo+hi)/2));
      }
    }
    return {p,poll,target,reached,fixed:[...fixed]};
  }
  function runoff(data,opts={},r1=null) {
    r1=r1??first(data,opts);
    const a=opts.a??r1.rank[0],b=opts.b??r1.rank[1],out=opts.out??0.03;
    if(out<0||out>=1) throw Error('Exclusión de segunda vuelta inválida');
    const pri=opts.precomputed??probabilities(data,opts.model??0,a,b,opts.poll??'fit',opts.cross??false);
    const shift=opts.shift??0;
    const p=pri.p.map(x=>logistic(logit(x)+shift));
    const stage2=Array.from({length:20},()=>[0,0,0]);
    // Las preferencias pueden seguir el voto simulado (supuesto Markov) o
    // el voto real de origen (invariancia de preferencias binarias).
    for(let i=0;i<18;i++) for(let j=0;j<20;j++) {
      const v=r1.flows[i][j];
      if(j>=18) {stage2[j][2]+=v;continue;}
      const pa=p[opts.memory==='origin'?i:j];
      stage2[j][0]+=v*(1-out)*pa;
      stage2[j][1]+=v*(1-out)*(1-pa);
      stage2[j][2]+=v*out;
    }
    // El blanco/nulo y la abstención de la elección real no se remobilizan.
    const g=opts.unit!=null?data.local_units[opts.unit]:data.geographies[opts.geo??0];
    stage2[18][2]+=g.votes[18];stage2[19][2]+=g.abstention??0;
    const totals=[0,1,2].map(k=>sum(stage2.map(r=>r[k])));
    const valid=totals[0]+totals[1];
    return {a,b,totals,valid,share:totals[0]/valid,stage2,probabilities:p,...pri};
  }
  const api={sum,first,runoff,preference,findPoll,probabilities,tilt,jointFit};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  root.Escenarios2003=api;
})(typeof globalThis!=='undefined'?globalThis:this);
