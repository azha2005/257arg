"""Publicación local autocontenida: datos y aplicación en un solo HTML."""
from pathlib import Path
import json
import pandas as pd
HERE=Path(__file__).resolve().parent

def enriquecer(data):
 sources={
  'rn':'https://www.jusrionegro.gov.ar/inicio/web/escrutinio-16-04-2023/',
  'neuquen':'https://intranet.jusneuquen.gov.ar/images2/Electoral/CP_16-04-2023/escrutinio_def/Escrutinio_DefinitivoxMesas_2023.pdf',
  'misiones':'https://www.electoralmisiones.gov.ar/wp-content/uploads/2023/05/Acta-Acuerdo-N%C2%B01166-Anexo-I.pdf',
  'salta':'https://www.electoralsalta.gov.ar/Elecciones/Escrutinio/Escrutinio-2023G.xlsx',
 }
 for d in data:
  if '_prov2025_' in d['id']:
   d['cobertura_provincial']=d['cobertura_origen']
  else:
   key=d['id'].split('_')[0];d['serie']='2023';d.setdefault('fuente',sources.get(key,''))
   if 'cobertura_provincial' in d:pass
   elif key=='neuquen':
    raw=pd.read_pickle(HERE.parent/'provinciales2023/prov_neuquen.pkl')
    crossed=pd.read_csv(HERE.parent/'provinciales2023/base_neuquen_gob2023.csv',index_col=0)
    d['cobertura_provincial']=float(crossed.values.sum()/raw.values.sum())
   elif key=='misiones':d['cobertura_provincial']=695488/695983
   else:d['cobertura_provincial']=1.
  folder=HERE/'resultados'/d['id']
  ctl={k:v for k,v in d.items() if k not in ['rows','cols','matriz','variante','pct','p05','p95','observado_destino','firma_insumos']}
  (folder/'control.json').write_text(json.dumps(ctl,ensure_ascii=False,indent=2),encoding='utf8')
  (folder/'resultado.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
 return data

def main():
 data=enriquecer(json.loads((HERE/'resultados.json').read_text(encoding='utf8')))
 (HERE/'resultados.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
 template=(HERE/'visor.html').read_text(encoding='utf8')
 css=(HERE/'estilo.css').read_text(encoding='utf8')
 for filename in ['tokens.css','base.css']:
  css=css.replace('@import url("./'+filename+'");',(HERE/filename).read_text(encoding='utf8'))
 template=template.replace('__ESTILO__',css)
 assert template.count('__DATA__')==1
 (HERE/'INDICE.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')),encoding='utf8')
 print('Visor',len(data),'cruces',HERE/'INDICE.html')
if __name__=='__main__':main()
