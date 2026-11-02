const {chromium}=require('C:/Users/JC/Downloads/elefanopus55/videoelefante/node_modules/playwright-core');
const assert=require('assert');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base='http://127.0.0.1:8793';
  await page.goto(base+'/mapas/mapa2003escenarios/index.html');
  await page.getByRole('link',{name:'Sin Carlos Menem',exact:true}).click();
  await page.waitForFunction(()=>window.__scenario);
  assert.equal(await page.inputValue('#s-retired'),'0');
  await page.selectOption('#s-retired','1');await page.selectOption('#s-stage','2');
  assert.equal(await page.evaluate(()=>window.__scenario.stage),2);
  assert.equal(await page.evaluate(()=>window.__scenario.opts.removed),1);
  await page.goto(base+'/analisis/escenarios2003/simulador_2003.html');
  await page.waitForFunction(()=>window.__simState);
  await page.selectOption('#removed','2');
  assert.equal(await page.evaluate(()=>window.__simState.o.removed),2);
  assert.equal(await page.locator('#error').textContent(),'');assert.equal(errors.length,0);
  console.log('HTTP: índice, apertura de atlas, cambio de candidatura/vuelta y simulador correctos; sin errores JS.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
