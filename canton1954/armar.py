from pathlib import Path
import json,re,csv
ROOT=Path(__file__).resolve().parent
BASE=['Inscriptos','Votantes','Partido Peronista','Unión Cívica Radical']
COM='Partido Comunista'; SOC='Partido Socialista (Revolución Nacional)'; DEM='Partido Demócrata'; PDP='Partido Demócrata Progresista'; BA='Blanco y Anulados'
GRUPOS=[
 ('Capital Federal',172,3,1,BASE+[SOC,COM,'Concentración Obrera',PDP,BA],'Diputados'),
 ('Buenos Aires',175,12,4,BASE+[DEM,SOC,COM,BA],'Diputados'),
 ('Catamarca',187,3,1,BASE+[BA],'Diputados'),
 ('Córdoba',190,3,1,BASE+[COM,BA],'Diputados'),
 ('Corrientes',193,3,1,BASE+[DEM,COM,BA],'Diputados'),
 ('Chaco',196,3,1,BASE+[COM,BA],'Diputados'),
 ('Chubut',199,3,1,BASE+[COM,BA],'Vicepresidente'),
 ('Entre Ríos',202,3,1,BASE+[COM,BA],'Diputados'),
 ('Formosa',205,3,1,BASE+[COM,BA],'Vicepresidente'),
 ('Jujuy',208,3,1,BASE+[SOC,BA],'Diputados'),
 ('La Pampa',211,3,1,BASE+[BA],'Diputados'),
 ('La Rioja',214,3,1,BASE+[BA],'Diputados'),
 ('Mendoza',217,3,1,BASE+[BA],'Diputados'),
 ('Misiones',220,3,1,BASE+[COM,BA],'Vicepresidente'),
 ('Neuquén',223,3,1,BASE+[COM,BA],'Vicepresidente'),
 ('Río Negro',226,3,1,BASE+[COM,BA],'Vicepresidente'),
 ('Salta',229,3,1,BASE+[COM,BA],'Diputados'),
 ('San Juan',232,3,1,BASE+[DEM,SOC,COM,BA],'Diputados'),
 ('San Luis',235,1,1,BASE+[DEM,BA],'Diputados'),
 ('Santa Cruz',236,3,1,BASE+[BA],'Delegados'),
 ('Santa Fe',239,3,1,BASE+[PDP,COM,BA],'Diputados'),
 ('Santiago del Estero',242,3,1,BASE+[SOC,COM,BA],'Diputados'),
 ('Tucumán',245,1,1,BASE+[DEM,COM,BA],'Diputados'),
 ('Comodoro Rivadavia',246,3,1,BASE+[COM,BA],'Vicepresidente'),
]

def agrupar(words):
    groups=[]
    for w in sorted(words,key=lambda w:w['y']+w['h']/2):
        y=w['y']+w['h']/2
        if not groups or y-groups[-1][0]>18: groups.append([y,[w]])
        else: groups[-1][1].append(w)
    return [(sum(w['y']+w['h']/2 for w in g)/len(g),' '.join(w['text'] for w in sorted(g,key=lambda w:w['x']))) for _,g in groups]

def main():
    out=ROOT/'borrador';out.mkdir(exist_ok=True)
    allpages=[]
    for prov,start,count,stride,cols,cargo in GRUPOS:
        for offset in range(count):
            p=start+offset
            cat=['varones solamente','mujeres solamente','varones y mujeres'][offset//stride] if count>1 else 'varones solamente'
            raw=json.loads((ROOT/f'revision/p_{p}_celdas.json').read_text(encoding='utf-8'))
            if not raw['columnas_ocr']: print('NO GRID',p);continue
            names=agrupar(raw['columnas_ocr'][0])
            names=[(y,t) for y,t in names if len(re.sub('[^A-Za-z]','',t))>=4 and y>raw['top']+92 and y<raw['bottom']-18]
            filas=[]
            for y,name in names:
                valores={}; literales={}; coords={}
                for i,col in enumerate(raw['columnas_ocr'][1:len(cols)+1],1):
                    near=[w for w in col if abs(w['y']+w['h']/2-y)<22]
                    token=''.join(w['text'] for w in near)
                    literales[str(i)]=token
                    val=re.sub('[^0-9]','',token)
                    valores[str(i)]=int(val) if val else None
                    coords[str(i)]={'x0':raw['limites_x'][i],'x1':raw['limites_x'][i+1],'y':y}
                filas.append({'departamento':name,'valores':valores,'literales_ocr':literales,'coordenadas':coords})
            page={'pagina_pdf':p,'pagina_libro':p+5,'anio':1954,'eleccion':cargo,'provincia':prov,'categoria':cat,'es_continuacion':(offset%stride)>0,'columnas':{str(i):c for i,c in enumerate(cols,1)},'filas':filas,'estado':'borrador OCR sin revisión completa'}
            (out/f'p_{p}.json').write_text(json.dumps(page,ensure_ascii=False,indent=2),encoding='utf-8')
            allpages.append(page)
    (ROOT/'revision/filas.txt').write_text('\n'.join(f"\nPDF {p['pagina_pdf']} {p['provincia']} {p['categoria']}\n"+'\n'.join(f"{i+1:2} {r['departamento']}: "+' '.join(str(v) if v is not None else '-' for v in r['valores'].values()) for i,r in enumerate(p['filas'])) for p in allpages),encoding='utf-8')
    print('Páginas',len(allpages),'filas',sum(len(p['filas']) for p in allpages))

if __name__=='__main__':main()
