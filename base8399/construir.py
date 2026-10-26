"""Arma base8399/elecciones/<AAAA>_<cargo>/ a partir del zip recopilado (extraido en SRC).
Capa 1 = Lupu-Stokes (nacional, familias ucr/pj). Capa 2 = detalle por partido (provincias sueltas).
Nada se corrige ni se imputa: solo se separa por eleccion y se normaliza el esquema."""
import csv, os, sys, collections
SRC = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'elecciones')
rd = lambda p: list(csv.DictReader(open(os.path.join(SRC, p), encoding='utf-8-sig')))
DET = ['provincia','anio','cargo','departamento','codigo_fuente','partido_fuente','votos','tipo_fila','fuente']
det = collections.defaultdict(list)   # (anio, cargo) -> filas
CARGO = {'Presidente':'presidente','Dip-Nac':'diputados','Diputados Nacionales':'diputados','1':'presidente'}

for r in rd('busqueda_ampliada/mendoza_nacionales_1983_1999.csv'):
    det[(r['anio'], CARGO[r['cargo_fuente']])].append(dict(provincia='Mendoza', anio=r['anio'], cargo=CARGO[r['cargo_fuente']],
        departamento=r['departamento'], codigo_fuente=r['departamento_id_fuente'], partido_fuente=r['partido_fuente'],
        votos=r['votos'], tipo_fila='agrupacion', fuente='UNCuyo '+r['archivo_fuente']))

NO_PART = {'995','996','997','998','999'}
for r in rd('cordoba_1999_datos/departamentos_original.csv'):
    for col, c in (('presidente_vice','presidente'),('diputados_nacionales','diputados')):
        det[('1999', c)].append(dict(provincia='Córdoba', anio='1999', cargo=c, departamento=r['unidad'],
            codigo_fuente=r['codigo_unidad'], partido_fuente=r['agrupacion_original'], votos=r[col],
            tipo_fila='total' if r['codigo_agrupacion']=='999' else ('tipo_voto' if r['codigo_agrupacion'] in NO_PART else 'agrupacion'),
            fuente='Justicia Electoral Córdoba TOTELES99.xls'))

for r in rd('provincias_iteracion/votos_nacionales_departamentales.csv'):
    c = CARGO[r['cargo']]
    det[(r['anio'], c)].append(dict(provincia=r['provincia'], anio=r['anio'], cargo=c, departamento=r['departamento'],
        codigo_fuente='', partido_fuente=r['agrupacion_original'], votos=r['votos'], tipo_fila=r['tipo_fila'], fuente=r['archivo_fuente']))

ls = collections.defaultdict(list)
for r in rd('datos_1983_1999_lupu_stokes/resultados_1983_1999.csv'):
    c = 'presidente' if r['pres']=='1.0' else 'diputados'
    ls[(str(int(float(r['year']))), c)].append(r)

man = []
for key in sorted(set(ls)|set(det), key=lambda k:(k[0], k[1])):
    y, c = key; d = os.path.join(OUT, f'{y}_{c}'); os.makedirs(d, exist_ok=True)
    rows = ls.get(key, [])
    if rows:
        with open(os.path.join(d,'lupu_stokes.csv'),'w',newline='',encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
            for r in rows: r = dict(r); r['year']=y; w.writerow(r)
    drows = det.get(key, [])
    if drows:
        with open(os.path.join(d,'detalle_partidos.csv'),'w',newline='',encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=DET); w.writeheader(); w.writerows(drows)
    provs = sorted({r['province'] for r in rows})
    dprov = sorted({r['provincia'] for r in drows})
    nls = {p: sum(1 for r in rows if r['province']==p) for p in provs}
    man.append(dict(anio=y, cargo=c, ls_filas=len(rows), ls_distritos=len(provs),
        detalle_provincias='; '.join(dprov), detalle_filas=len(drows),
        ls_provincias=len(provs)))
with open(os.path.join(os.path.dirname(OUT),'manifest.csv'),'w',newline='',encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(man[0].keys())); w.writeheader(); w.writerows(man)
for m in man: print(m)
