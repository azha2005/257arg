from pathlib import Path
import csv, json, shutil, concurrent.futures, urllib.request, datetime
import pymupdf as fitz

ROOT=Path(__file__).resolve().parent
F=ROOT/'fuentes'; F.mkdir(exist_ok=True)
DATE='2026-10-15'
SPECS=[('Buenos Aires','19-d',4),('Catamarca','28-p',5),('Corrientes','51-d',8),('Entre Ríos','46-d',9),('Mendoza','42-d',105),('Salta','49-d',19),('San Juan','27-d',82),('San Luis','44-d',13),('Santa Fe','17-d',30),('Tucumán','26-p',112),('Tucumán','26-d',112)]
SPECS += [('Capital Federal','12-d',7),('Córdoba','3-d',6)]
def get(spec):
    prov,exp,page=spec
    url=f'https://apym.hcdn.gob.ar/uploads/expedientes/pdf/{exp}-1912.pdf'
    name=prov.lower().replace(' ','_')+'_'+exp+'-1912.pdf'
    dest=F/name; local=Path.home()/'Downloads'/(exp+'-1912.pdf')
    status=''; error=''
    if dest.exists():
        status='copia conservada de esta búsqueda'
    elif local.exists():
        shutil.copy2(local,dest); status='copia local recuperada; URL no revalidada'
    else:
        for attempt in range(2):
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'InvestigacionElectoral1912/1.0 (fuentes historicas; usuario Commons ItsAHardLife)'})
                with urllib.request.urlopen(req,timeout=22) as r: data=r.read()
                if not data.startswith(b'%PDF'): raise ValueError('respuesta no PDF')
                dest.write_bytes(data); status='descargado'; break
            except Exception as e: error=repr(e)
    pages=''
    if dest.exists():
        try:
            d=fitz.open(dest); pages=len(d)
            (F/(dest.stem+'.txt')).write_text('\n'.join(f'\n--- PDF {i+1} ---\n'+p.get_text() for i,p in enumerate(d)),encoding='utf-8')
            for i in set([0,page-1]):
                if i<len(d): d[i].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(str(F/(dest.stem+f'_p{i+1}.png')))
        except Exception as e: status='archivo inválido';error=repr(e)
    return dict(fuente_id=exp+'-1912',provincia=prov,url=url,fecha_consulta=DATE,archivo=name if dest.exists() else '',tamano=dest.stat().st_size if dest.exists() else 0,estado=status or 'fallo tras dos intentos',paginas=pages,error=error)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: rows=list(ex.map(get,SPECS))
    with (ROOT/'fuentes.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    print(json.dumps(rows,ensure_ascii=False,indent=2))
