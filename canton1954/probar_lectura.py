from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'deps'))
from rapidocr_onnxruntime import RapidOCR
import cv2,numpy as np
from controlar import manual,norm
from armar import agrupar
import difflib
engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2,rec_model_path=str(ROOT/'en_number_mobile_v2.0_rec_infer.onnx'),rec_img_shape=[3,32,320])
man=manual();allreads=[]
for mode in range(5):
    crops=[];truth=[]
    for p in [187,188]:
        raw=json.loads((ROOT/f'revision/p_{p}_celdas.json').read_text(encoding='utf-8'))
        image=cv2.imread(str(ROOT/f'revision/p_{p}.png'))
        clean=cv2.imread(str(ROOT/f'revision/p_{p}_ocr.png'))
        names=agrupar(raw['columnas_ocr'][0])
        for row in man[p]:
            y,t=max(names,key=lambda z:difflib.SequenceMatcher(None,norm(z[1]),norm(row['departamento'])).ratio())
            for c,value in row['valores'].items():
                if value is None:continue
                ci=int(c);x0,x1=raw['limites_x'][ci:ci+2]
                hh=20 if mode==0 else 15
                margin=4 if mode==0 else 10
                a=(clean if mode==4 else image)[round(y)-hh:round(y)+hh+1,x0+margin:x1-margin]
                if mode in (2,3):
                    gray=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
                    if mode==2:
                        bg=cv2.GaussianBlur(gray,(0,0),8)
                        gray=cv2.divide(gray,bg,scale=255)
                        a=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
                    else:
                        bw=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
                        a=cv2.cvtColor(bw,cv2.COLOR_GRAY2BGR)
                crops.append(a);truth.append(value)
    results,_=engine.text_rec(crops)
    reads=[int(re.sub('[^0-9]','',t)) if re.sub('[^0-9]','',t) else None for t,_ in results]
    allreads.append(reads)
    print(mode,sum(x==y for x,y in zip(reads,truth)),len(truth),flush=True)
from collections import Counter
vote=[Counter(vs).most_common(1)[0][0] for vs in zip(*allreads)]
print('Voto',sum(x==y for x,y in zip(vote,truth)),len(truth))
