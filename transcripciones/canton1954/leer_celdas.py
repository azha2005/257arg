"""Segunda lectura local independiente; no envía el documento a servicios."""
from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'deps'))
from rapidocr_onnxruntime import RapidOCR
import cv2

engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2)
for file in sorted((ROOT/'transcripcion').glob('p_*.json')):
    page=json.loads(file.read_text(encoding='utf-8'))
    p=page['pagina_pdf']
    if len(sys.argv)>1 and p not in {int(v) for v in sys.argv[1:]}:continue
    if page['estado']=='transcripción visual':continue
    raw=json.loads((ROOT/f'revision/p_{p}_celdas.json').read_text(encoding='utf-8'))
    image=cv2.imread(str(ROOT/f'revision/p_{p}.png'))
    crops=[];keys=[]
    for row in page['filas']:
        sourcep=row.get('pagina_fuente',p)
        raw=json.loads((ROOT/f'revision/p_{sourcep}_celdas.json').read_text(encoding='utf-8'))
        image=cv2.imread(str(ROOT/f'revision/p_{sourcep}.png'))
        y=row['y']
        for c in row['valores']:
            if row['literales'][c] in ('*','**'):continue
            ci=int(c); x0,x1=raw['limites_x'][ci:ci+2]
            crops.append(image[max(0,round(y)-20):round(y)+21,max(0,x0+4):x1-4])
            keys.append((row['departamento'],c))
    results,_=engine.text_rec(crops)
    out={}
    for (name,c),(text,conf) in zip(keys,results):
        num=re.sub('[^0-9]','',text)
        out.setdefault(name,{})[c]={'literal':text,'valor':int(num) if num else None,'confianza':float(conf)}
    (ROOT/f'revision/p_{p}_rapid.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(p,flush=True)
