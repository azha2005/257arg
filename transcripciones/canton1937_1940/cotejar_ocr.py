"""Lectura OCR independiente para localizar posibles errores de digitación visual."""
from pathlib import Path
import sys, json, re, difflib, unicodedata
import cv2
from exportar import load, ROOT, PROJECT
sys.path.insert(0,str(PROJECT/'canton1954/deps'))
from rapidocr_onnxruntime import RapidOCR


def norm(s):
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s.casefold()).encode('ascii','ignore').decode())


def main():
    engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2)
    out=ROOT/'cotejo';out.mkdir(exist_ok=True)
    differences=[]
    for p in load():
        n=p['pagina_pdf']
        if len(sys.argv)>1 and n not in set(map(int,sys.argv[1:])):continue
        folder=PROJECT/'canton1946' if n>=153 else ROOT
        cache=out/f'p_{n}_rapid.json'
        if cache.exists():words=json.loads(cache.read_text(encoding='utf-8'))
        else:
            results,_=engine(str(folder/f'revision/p_{n}.png'))
            words=[{'text':t,'conf':float(conf),'x':float(sum(v[0] for v in box)/4),'y':float(sum(v[1] for v in box)/4),'box':box} for box,t,conf in results]
            cache.write_text(json.dumps(words,ensure_ascii=False,indent=2),encoding='utf-8')
        groups=[]
        for w in sorted([w for w in words if w['x']<390 and 220<w['y']<2010 and not re.fullmatch(r'[\d., ]+',w['text'])],key=lambda w:w['y']):
            if not groups or w['y']-groups[-1][0]>20:groups.append([w['y'],[w]])
            else:groups[-1][1].append(w)
        for r in p['filas']:
            candidates=[]
            for yy,ws in groups:
                text=' '.join(w['text'] for w in ws)
                score=difflib.SequenceMatcher(None,norm(r['unidad']),re.sub(r'\d','',norm(text))).ratio()
                candidates.append((score,yy,text))
            score,y,label=max(candidates)
            if score<.60:
                differences.append({'pagina':n,'unidad':r['unidad'],'tipo':'fila no reconocida','score':score});continue
            cells=sorted([w for w in words if w['x']>390 and abs(w['y']-y)<20],key=lambda w:w['x'])
            vals=[]
            for w in cells:
                token=re.sub('[^0-9]','',w['text'])
                vals.append(int(token) if token else None)
            expected=list(r['valores'].values())
            if vals!=expected:
                differences.append({'pagina':n,'unidad':r['unidad'],'y':y,'etiqueta_ocr':label,'manual':expected,'ocr':vals,'tipo':'lecturas distintas','ocr_textos':[w['text'] for w in cells]})
        print(n,flush=True)
    (out/'diferencias.json').write_text(json.dumps(differences,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Diferencias',len(differences),flush=True)


if __name__=='__main__':main()
