"""Controles de conservación, cobertura, interfaz y exportaciones."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
EDGE=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

def verificar_datos():
 data=json.loads((HERE/'resultados.json').read_text(encoding='utf8'))
 bases={}
 for folder in ['provinciales2023','provinciales2025','provinciales/circuitos']:
  bases.update(pd.read_pickle(HERE.parent/folder/'bases.pkl'))
 assert len(data)==len(bases) and len(data)>=25
 checks=[]
 for d in data:
  a,b,c=bases[d['id']];folder=HERE/'resultados'/d['id']
  assert a.index.equals(b.index) and a.index.is_unique
  assert (a.values>=0).all() and (b.values>=0).all()
  for name,t in [('origen_observado',a),('destino_observado',b)]:
   stored=pd.read_csv(folder/(name+'.csv'),index_col=0)
   assert list(stored.columns)==list(t.columns)
   np.testing.assert_allclose(stored.values,t.values)
  B=pd.read_csv(folder/'matriz_pct.csv',index_col=0).values/100
  M=pd.read_csv(folder/'matriz_votos.csv',index_col=0).values
  C=pd.read_csv(folder/'variante_pct.csv',index_col=0).values/100
  lo=np.array(d['p05']);hi=np.array(d['p95'])
  assert np.isfinite(B).all() and (B>=0).all() and (C>=0).all()
  np.testing.assert_allclose(B.sum(1),1,atol=1e-10)
  np.testing.assert_allclose(C.sum(1),1,atol=1e-10)
  mass=(a.div(a.sum(1),axis=0).values*b.sum(1).values[:,None]).sum(0)
  np.testing.assert_allclose(M.sum(1),mass,rtol=1e-10)
  np.testing.assert_allclose(M.sum(),b.values.sum(),rtol=1e-10)
  assert (lo<=hi).all() and (lo>=0).all() and (hi<=100).all()
  assert d['bootstrap']==200 and len(d['filas'])==len(a.columns)
  for f in d.get('foco',[]):assert f in a.columns or f in b.columns,(d['id'],f)
  if d['id'].startswith('sanluis'):assert all(f['no_identificada'] for f in d['filas'])
  checks.append(dict(id=d['id'],unidades=len(a),origen=int(a.values.sum()),destino=int(b.values.sum()),
   cobertura_provincial=d['cobertura_provincial'],filas_inciertas=sum(f['no_identificada'] for f in d['filas']),
   conservacion=True,matrices_estocasticas=True))
 return data,checks

def verificar_visor(data):
 exports=HERE/'exportados';exports.mkdir(exist_ok=True)
 screenshots=HERE/'img';screenshots.mkdir(exist_ok=True)
 errors=[];checks=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True)
  page=browser.new_page(viewport={'width':1500,'height':1100},device_scale_factor=1)
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto((HERE/'INDICE.html').as_uri())
  for d in data:
   page.evaluate('(d)=>loadSeries(d.serie,d.nombre,d.id)',dict(serie=d['serie'],nombre=d['nombre'],id=d['id']))
   assert page.locator('#chart path[data-flow]').count()>0,d['id']
   assert page.locator('#chart [data-node]').count()==len(d['rows'])+len(d['cols'])
   # Labels must remain within the SVG; full labels also survive in <title>.
   outside=page.evaluate('''() => {let s=document.getElementById('chart'),v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].filter(t=>{let b=t.getBBox();return b.x<0||b.x+b.width>v.width+1||b.y<0||b.y+b.height>v.height+1}).map(t=>t.textContent)}''')
   assert not outside,(d['id'],outside)
   overlaps=page.evaluate('''() => ['o','d'].flatMap(side=>{let boxes=[...document.querySelectorAll('[data-node^="'+side+'"]')].map(g=>{let ts=[...g.querySelectorAll('text')].map(t=>t.getBBox());return {name:g.getAttribute('aria-label'),top:Math.min(...ts.map(b=>b.y)),bottom:Math.max(...ts.map(b=>b.y+b.height))}}).sort((a,b)=>a.top-b.top);return boxes.slice(1).filter((b,i)=>b.top<boxes[i].bottom+1).map((b,i)=>b.name)})''')
   assert not overlaps,(d['id'],overlaps)
   for mode in ['principal','calvo']:
    page.select_option('#variant',mode)
    for which in ['o0','d0','']:
     page.select_option('#focus',which)
     assert page.locator('#profile tbody tr').count()>0
   page.select_option('#variant','principal');page.select_option('#focus','')
   text=page.evaluate('svgText()')
   (exports/(d['id']+'.svg')).write_text(text,encoding='utf8')
   page.locator('#chart').screenshot(path=str(exports/(d['id']+'.png')))
   if d['id'] in ['pba_prov2025_dn2025','rn_gob2023_2023b','salta_diputado_prov2025_dn2025']:
    page.screenshot(path=str(screenshots/(d['id']+'.png')),full_page=True)
   checks.append(dict(id=d['id'],flujos=page.locator('#chart path[data-flow]').count(),rotulos_dentro=True,variantes=True,seleccion_bidireccional=True))
  page.evaluate("loadSeries('2025','Formosa')")
  assert page.locator('#content').is_hidden()
  assert 'Pendiente' in page.locator('#warning').inner_text()
  # Exercise the actual download buttons, not only internal serializers.
  page.evaluate("loadSeries('2025','Buenos Aires')")
  for button,ext in [('svgexport','svg'),('pngexport','png'),('csvexport','csv')]:
   with page.expect_download() as event:page.click('#'+button)
   dl=event.value;dl.save_as(str(exports/('verificacion_descarga.'+ext)))
   assert (exports/('verificacion_descarga.'+ext)).stat().st_size>100
  browser.close()
 assert not errors,errors
 return checks

if __name__=='__main__':
 data,checks=verificar_datos();ui=verificar_visor(data)
 report=dict(cruces=len(data),distritos_2025_con_datos=9,distritos_2025_pendientes=['Formosa'],
  datos=checks,visor=ui,descargas=['SVG','PNG','CSV'],errores_javascript=[],
  alcance='Resultados locales; la validación numérica y visual no valida elecciones individuales ni elimina sesgo ecológico.')
 (HERE/'VALIDACION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print('VALIDACIÓN',len(checks),'cruces;',len(ui),'gráficos; SVG/PNG/CSV correctos',flush=True)
