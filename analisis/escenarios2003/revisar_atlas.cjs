const {chromium}=require('C:/Users/JC/Downloads/elefanopus55/videoelefante/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
const out=path.resolve(__dirname,'../../mapas/mapa2003escenarios'),files=JSON.parse(fs.readFileSync(path.join(out,'manifiesto.json'),'utf8'));
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1920,height:1800}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 let switches=0,maxError=0;
 for(const file of files){
  await page.goto('file:///'+path.join(out,file.html).replaceAll('\\','/'));
  await page.waitForFunction(()=>window.__scenario,{timeout:20000});
  const initial=await page.evaluate(()=>({id:DATA.slug,retired:ATLAS_INPUT.sim.candidates[window.__scenario.opts.removed].id,units:DATA.modes[0].units.length,controls:document.querySelector('#scenario-controls').textContent}));
  assert.equal(initial.retired,file.id);assert.equal(initial.units,540);
  for(const model of ['0','1','2','3'])for(const stage of ['0','1','2']){
   await page.selectOption('#s-model',model);await page.selectOption('#s-stage',stage);
   for(const mode of ['gan','voto','margen']){
    const s=await page.evaluate(mode=>{window.__atlas.setMode(mode);const rows=DATA.modes.find(m=>m.id==='gan').units;const totals={};for(const r of rows)for(const [c,v]of r.lines||[])totals[c]=(totals[c]||0)+v;const scenario=window.__scenario;const target=+scenario.stage===2?[scenario.second.a,scenario.second.b]:Array.from({length:18},(_,i)=>i);const errors=target.map(i=>Math.abs((totals[ATLAS_INPUT.sim.candidates[i].id]||0)-(+scenario.stage===0?ATLAS_INPUT.sim.geographies[0].votes[i]:+scenario.stage===1?scenario.first.totals[i]:scenario.second.totals[i===scenario.second.a?0:1])));return{missing:rows.filter(r=>!r.w).length,nan:rows.some(r=>r.w&&!Number.isFinite(r.q)),maxError:Math.max(...errors),status:document.querySelector('#scenario-status').textContent,mode:window.__atlas.mode};},mode);
    assert.equal(s.missing,3);assert.equal(s.nan,false);assert.equal(s.mode,mode);assert(s.maxError<.05,JSON.stringify(s));maxError=Math.max(maxError,s.maxError);switches++;
   }
  }
  console.log('Verificado',file.id,switches,'cambios');
 }
 await page.goto('file:///'+path.join(out,files[0].html).replaceAll('\\','/')+'#bare-white-m-gan');await page.waitForFunction(()=>window.__scenario);
 await page.locator('#atlas').screenshot({path:path.join(out,'revision_primera.png')});
 await page.evaluate(()=>{const s=document.querySelector('#s-stage');s.value='2';s.dispatchEvent(new Event('change',{bubbles:true}));});await page.locator('#atlas').screenshot({path:path.join(out,'revision_balotaje.png')});
 for(const stage of ['1','2'])for(const mode of ['voto','margen']){
  await page.evaluate(({stage,mode})=>{const s=document.querySelector('#s-stage');s.value=stage;s.dispatchEvent(new Event('change',{bubbles:true}));window.__atlas.setMode(mode);},{stage,mode});
  await page.locator('#atlas').screenshot({path:path.join(out,`revision_${stage}_${mode}.png`)});
 }
 await page.goto('file:///'+path.join(out,files[0].html).replaceAll('\\','/'));await page.waitForFunction(()=>window.__scenario);
 await page.selectOption('#s-poll','may');await page.selectOption('#s-pair','0-1');assert.equal(await page.inputValue('#s-pair'),'auto');
 await page.selectOption('#s-local','province');await page.selectOption('#s-local','local');
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'revision_movil.png')});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert(overflow<=1,`Overflow ${overflow}`);
 await browser.close();assert.equal(errors.length,0,errors.join('\n'));
 const result={atlas:files.length,mode_switches:switches,max_aggregation_error:maxError,js_errors:errors,mobile_overflow:overflow};
 fs.writeFileSync(path.join(out,'revision_automatizada.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1});
