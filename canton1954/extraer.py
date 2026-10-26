"""Asistente local de transcripción: conserva OCR, posiciones y originales.

El OCR no es una transcripción verificada. Las correcciones se aplican aparte.
"""
from pathlib import Path
import json
import argparse
import concurrent.futures
import cv2
import numpy as np
import pymupdf
import pytesseract

ROOT = Path(__file__).resolve().parent
PDF = ROOT.parent / 'raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pagina(n):
    dest = ROOT / 'revision'
    dest.mkdir(exist_ok=True)
    with pymupdf.open(PDF) as doc:
        p = doc[n-1]
        pix = p.get_pixmap(matrix=pymupdf.Matrix(3,3))
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height,pix.width,3).copy()
    gray = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    edges=cv2.Canny(gray,80,180)
    hl=cv2.HoughLinesP(edges,1,np.pi/1800,threshold=180,minLineLength=600,maxLineGap=30)
    angles=[]
    if hl is not None:
        for x1,y1,x2,y2 in hl[:,0]:
            angle=np.degrees(np.arctan2(y2-y1,x2-x1))
            if abs(abs(angle)-90)<4:
                angles.append(angle-90 if angle>0 else angle+90)
    angle=float(np.median(angles)) if angles else 0
    if abs(angle)>.03:
        mat=cv2.getRotationMatrix2D((gray.shape[1]/2,gray.shape[0]/2),angle,1)
        a=cv2.warpAffine(a,mat,(gray.shape[1],gray.shape[0]),borderValue=(255,255,255))
        gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    bw = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,35,15)
    vert = cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,100)))
    horiz = cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(120,1)))
    lines = cv2.bitwise_or(vert,horiz)
    clean = cv2.bitwise_not(cv2.subtract(bw,cv2.dilate(lines,np.ones((2,2),np.uint8))))
    hc,_=cv2.findContours(horiz,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    hr=[cv2.boundingRect(c) for c in hc if cv2.boundingRect(c)[2]>a.shape[1]*.75]
    contours,_ = cv2.findContours(vert,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    rects=sorted([cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[3] > a.shape[0]*.40])
    xs=[]
    for x,y,w,h in rects:
        if not xs or x-xs[-1]>25:
            xs.append(x+w//2)
    # Keep the observed rules before reconstructing faint outer borders.
    observed=[x for x in xs if 40<x<a.shape[1]-25]
    # The printed form has eleven equally spaced numeric columns and a
    # department column three times as wide. Recover broken/faint rules.
    if hr:
        header=min(hr,key=lambda r:r[1])
        left,hy,width,hh=header
        right=left+width-2
        vx=[x for x in xs if x>a.shape[1]*.20 and x<right+12]
        if len(vx)>3:
            ks=np.round((right-np.array(vx))/106.5)
            slope,intercept=np.polyfit(ks,np.array(vx),1)
            xs=[left]+[int(round(intercept+slope*k)) for k in range(11,-1,-1)]
        else:
            step=width/14
            xs=[left]+[int(round(left+step*k)) for k in range(3,15)]
    elif len(xs)>5:
        diffs=np.diff(xs)
        step=float(np.median(diffs[(diffs>85)&(diffs<125)]))
        right=xs[-1]
        xs=[int(round(right-step*14))]+[int(round(right-step*k)) for k in range(11,-1,-1)]
    table={'limites_x':xs,'columnas_ocr':[], 'angulo':angle}
    if n in (196,217,227,237):
        # Book gutter/curved rules interrupt the automatic line detector.
        fallback={196:(66,1560,150,1600),217:(88,1570,170,1610),227:(100,1608,210,1640),237:(126,1630,210,1640)}
        left,right,top,bottom=fallback[n]
        step=(right-left)/14
        xs=[left]+[round(right-step*k) for k in range(11,-1,-1)]
        table['limites_x']=xs
    if n!=171:
        numleft=next((x for x in observed if 325<x<510),None)
        if numleft is None:
            numleft={196:383,217:405,227:440}.get(n,400)
        regular=[x for x in observed if numleft-10<=x<=numleft+1200]
        if len(regular)>3:
            ks=np.round((np.array(regular)-numleft)/106.5)
            step,origin=np.polyfit(ks,np.array(regular),1)
        else:step,origin=106.5,numleft
        xs=[round(origin-3*step)]+[round(origin+step*k) for k in range(12)]
        table['limites_x']=xs
    if len(xs)>3 and n!=171:
        top=min([r[1] for r in hr]+[r[1] for r in rects if 110<r[1]<350]) if hr else int(np.median([r[1] for r in rects]))
        bottom=max(r[1] for r in hr) if len(hr)>1 else (max(r[1]+r[3] for r in rects) if rects else 1640)
        if n in (196,217,227,237):
            _,_,top,bottom=fallback[n]
        top,bottom=130,a.shape[0]-130
        whole=json.loads((dest/f'p_{n}_ocr.json').read_text(encoding='utf-8')) if (dest/f'p_{n}_ocr.json').exists() else []
        stops=[w['top'] for w in whole if w['top']>1400 and w['text'].lower().strip(' :.,') in ('clave','clava','claves')]
        if stops: bottom=min(stops)-20
        table.update(top=top,bottom=bottom)
        for j,(x0,x1) in enumerate(zip(xs,xs[1:])):
            crop=clean[top+75:bottom-8,x0+9:x1-8]
            if False and j:
                # Remove punctuation/noise by glyph height before recognition;
                # otherwise typewriter thousands dots are often read as 6.
                nn,lab,stats,_=cv2.connectedComponentsWithStats(255-crop)
                mask=np.zeros_like(crop)
                for z in range(1,nn):
                    if stats[z,cv2.CC_STAT_HEIGHT]>=10 and stats[z,cv2.CC_STAT_AREA]>=12:
                        mask[lab==z]=255
                crop=255-mask
            cfg='--tessdata-dir canton1954/tessdata --psm 6'
            dd=pytesseract.image_to_data(crop,config=cfg,output_type=pytesseract.Output.DICT)
            table['columnas_ocr'].append([{'text':t,'x':dd['left'][i]+x0+9,'y':dd['top'][i]+top+75,'h':dd['height'][i],'conf':dd['conf'][i]} for i,t in enumerate(dd['text']) if t.strip()])
    (dest/f'p_{n}_celdas.json').write_text(json.dumps(table,ensure_ascii=False,indent=2),encoding='utf-8')
    cv2.imwrite(str(dest/f'p_{n}_ocr.png'),clean)
    data = pytesseract.image_to_data(clean,config='--psm 6',output_type=pytesseract.Output.DICT)
    words = [{k:data[k][i] for k in ['text','left','top','width','height','conf','block_num','par_num','line_num']} for i,t in enumerate(data['text']) if t.strip()]
    (dest/f'p_{n}_ocr.json').write_text(json.dumps(words,ensure_ascii=False,indent=2),encoding='utf-8')
    txt = pytesseract.image_to_string(clean,config='--psm 6')
    (dest/f'p_{n}_ocr.txt').write_text(txt,encoding='utf-8')
    # Original render remains the visual authority.
    cv2.imwrite(str(dest/f'p_{n}.png'),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
    return n

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('pages',type=int,nargs='*')
    args=parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for n in pool.map(pagina,args.pages or range(171,249)):
            print(n,flush=True)
