"""Reintentos públicos, sin autenticación ni evasión de controles."""
from pathlib import Path
import concurrent.futures as cf
import requests
import urllib3
urllib3.disable_warnings()
RAW=Path(__file__).resolve().parent/'fuentes'
URLS={
 'chaco_historico.html':'https://resultados.electoralchaco.gob.ar/historico/',
 'chaco_filtro.js':'https://resultados.electoralchaco.gob.ar/static/js/filtro_elecciones.bebce5cc10d0.js',
 'formosa_prueba.pdf':'http://archivostep.jusformosa.gob.ar/archivos/archivo_1752760038.pdf',
 'formosa_https.pdf':'https://archivostep.jusformosa.gob.ar/archivos/archivo_1752760038.pdf',
}
def get(kv):
 name,url=kv
 try:
  r=requests.get(url,timeout=25,verify=False,headers={'User-Agent':'Mozilla/5.0'})
  print(name,r.status_code,len(r.content),flush=True)
  if r.ok:(RAW/name).write_bytes(r.content)
 except requests.RequestException as e:print(name,type(e).__name__,flush=True)
if __name__=='__main__':
 s=requests.Session()
 try:
  r=s.get('https://tep.jusformosa.gob.ar/resultados',timeout=25)
  print('Formosa inicio',r.status_code,len(r.content),flush=True)
  r=s.get(URLS['formosa_https.pdf'],timeout=25,headers={'Referer':'https://tep.jusformosa.gob.ar/resultados'})
  print('Formosa PDF sesión',r.status_code,len(r.content),flush=True)
  if r.ok:(RAW/'formosa_seccion.pdf').write_bytes(r.content)
 except requests.RequestException as e:print('Formosa',type(e).__name__,flush=True)
