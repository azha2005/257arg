"""Datos 2009: PolAr, con reemplazo íntegro de TDF por el definitivo DINE."""
from pathlib import Path
import ast, json, sys, re
import pandas as pd
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'wikileg'))
from bloques_prov import match_prov
groups, mapping, log, totals = match_prov(2009, 'DIPUTADOS')
lookup = {g['grupo']: g for g in groups}

def find(fragment):
    return next(g['grupo'] for g in groups if fragment.lower() in g['grupo'].lower())

corrections = {
    ('Misiones', 'AL. FTE. JUSTICIAL. POR LA DIGNIDAD Y EL PROG'): 'kirchnerismo',
    ('Santiago del Estero', 'AL. ACUERDO CIVICO - FTE. UNIDAD POPULAR'): 'Acuerdo Cívico',
    ('Corrientes', 'ENC. CORRIENTES - ACUERDO CIVICO Y SOCIAL'): 'Acuerdo Cívico',
    ('Misiones', 'AL. FTE. DE LA ESPERANZA'): 'Movimiento de Integración',
    ('Corrientes', 'DEMOCRATA PROGRESISTA'): 'Acuerdo Cívico',
}
for k, fragment in corrections.items():
    mapping[k] = find(fragment)

votes, mesas = pd.read_pickle(ROOT/'datos_oficiales/2009/agregado_polar.pkl')
votes = votes[votes.cargo_nombre.str.contains('DIPUTAD')].copy()
mesas = mesas[mesas.cargo_nombre.str.contains('DIPUTAD')].copy()

# Planilla recuperada: se conserva completa y sin alterar en complementos/.
# PBA: reemplazo de TODAS las listas por la misma fuente para evitar mezclar escrutinios.
local = pd.read_excel(ROOT/'datos_oficiales/2009/complementos/merged_file_15_original.xls',sheet_name='Sheet1')
local = local[(local.anio==2009)&(local.eleccion=='DN')].copy()
pba = local[local.provinciaId==2].copy()
# Error de código de la planilla: General Alvarado figura 40, duplicando General Alvear.
# El nombre y PolAr identifican General Alvarado como 039. No se agregan ambas unidades.
pba.loc[pba.departamento.str.strip()=='GENERAL ALVARADO','departamentoId']=39
bad_decimal = pba.votos % 1 != 0
assert set(pba.loc[bad_decimal,'departamentoId']) == {51}
pba.loc[bad_decimal,'votos'] *= 1000
pba['votos'] = pba.votos.astype(int)
for sec,g in pba.groupby('departamentoId'):
    assert g[g.partidoId<990].votos.sum() == g[g.partidoId==990].votos.sum(), sec
    assert g[g.partidoId.isin([990,991,992])].votos.sum() == g[g.partidoId==994].votos.sum(), sec
party_pba = {
 14:'OBRERO',
}
# Correspondencia explícita de denominaciones: las numeraciones de lista de las dos fuentes difieren.
pba_names = {
 'ACUERDO CIVICO Y SOCIAL':'ACUERDO CIVICO Y SOCIAL', 'AUTENTICO':'AUTENTICO',
 'CONCERTACION PLURAL':'CONCERTACION PLURAL','FTE. ES POSIBLE':'FTE. ES POSIBLE',
 'FTE. JUSTICIALIS.P/LA VICTORIA':'FTE. JUSTICIALISTA PARA LA VICTORIA',
 'FTE. PTS - MAS IZQUIERDA SOCIALISTA':'PTS - MAS - IZQUIERDA SOCIALISTA',
 'MO.FE.JU. - MOV. FED. DE LOS JUB.':'MOV. FED. DE LOS JUBILADOS',
 'MOV. POP. PARA LA RECONQUISTA':'MOV. POP. DE LA RECONQUISTA',
 'MST - MIJD - NUEVA IZQ. EN UNIDAD':'MST-MIJD-NUEVA IZQUIERDA EN UNIDAD',
 'NE - NUEVO ENCUENTRO':'NUEVO ENCUENTRO', 'NUC - NUEVA UNION CIUDADANA':'NUEVA UNION CIUDADANA',
 'OBRERO':'OBRERO', 'PASIB - P. AC.SOL. INDEPENDIENTE':'P/ ACCION SOLIDARIA INDEP. BONAERENSE',
 'POPULAR DE LA RECONSTRUCCION':'POPULAR DE LA RECONSTRUCCION',
 'RENOVADOR DE LA PCIA. DE BS. AS.':'RENOVADOR DE BUENOS AIRES',
 'UNION - PRO':'UNION PRO', 'VECINALISTA DE INT. CIUDADANA':'VECINALISTA DE INTEG. CIUDADANA',
 'VIDA - VOL. P / INT. DES. AUT. ENT.':'VOLUNTAD P/INTEG. DESARR. AUTENTICO',
}
aid_by_name = dict(zip(votes[votes.distrito_id=='02'].agrupacion_nombre, votes[votes.distrito_id=='02'].agrupacion_id))
aid_by_name['NUEVO ENCUENTRO']='N508'
mapping[('Buenos Aires','NUEVO ENCUENTRO')] = find('Nuevo Encuentro')
sec_names = dict(zip(votes[votes.distrito_id=='02'].seccion_id, votes[votes.distrito_id=='02'].seccion_nombre))
add = []
for r in pba.itertuples():
    if r.partidoId in (990,994): continue
    sec = str(r.departamentoId).zfill(3)
    typ = {991:'BLANCO',992:'NULO'}.get(r.partidoId,'POSITIVO')
    nm = pba_names[r.partido.strip()] if typ=='POSITIVO' else ''
    add.append(dict(distrito_id='02',distrito_nombre='Buenos Aires',seccion_id=sec,
                    seccion_nombre=sec_names[sec],agrupacion_id=aid_by_name[nm] if nm else '',
                    agrupacion_nombre=nm,votos_tipo=typ,v=r.votos,cargo_nombre='DIPUTADOS NACIONALES'))
votes = pd.concat([votes[votes.distrito_id!='02'],pd.DataFrame(add)],ignore_index=True)

# Valle Grande (Jujuy): todas las listas, positivos, blancos y nulos de la planilla recuperada.
vg = local[(local.provinciaId==10)&(local.departamentoId==8)]
assert vg[vg.partidoId<990].votos.sum()==1734
vg_map={14:'Partido Obrero',38:'Movimiento Socialista de los Trabajadores',45:'Frente de Izquierda',
        501:'Peronismo Federal',503:'Peronismo Federal',504:'Acuerdo Cívico',505:'kirchnerismo',506:'kirchnerismo'}
add=[]
for r in vg.itertuples():
    if r.partidoId in (990,994): continue
    typ={991:'BLANCO',992:'NULO'}.get(r.partidoId,'POSITIVO')
    nm=r.partido.strip() if typ=='POSITIVO' else ''
    if nm: mapping[('Jujuy',nm)]=find(vg_map[r.partidoId])
    add.append(dict(distrito_id='10',distrito_nombre='Jujuy',seccion_id='008',seccion_nombre='Valle Grande',
                    agrupacion_id='JV%d'%r.partidoId if nm else '',agrupacion_nombre=nm,votos_tipo=typ,
                    v=int(r.votos),cargo_nombre='DIPUTADOS NACIONALES'))
votes=pd.concat([votes[~((votes.distrito_id=='10')&(votes.seccion_id=='008'))],pd.DataFrame(add)],ignore_index=True)

# Reemplazo por provincia completa: no mezclar partidos provisorios y definitivos en una unidad.
votes = votes[votes.distrito_id != '24'].copy()
names = ['JUSTICIALISTA', 'UNION CIVICA RADICAL', 'INTRANSIGENTE', 'HUMANISTA',
         'MOV. POPULAR FUEGUINO', 'FEDERAL FUEGUINO', 'POPULAR', 'ESPACIO TOTAL',
         'PROYECTO SUR', 'HACER POR TIERRA DEL FUEGO', 'COMPROMISO RENOVACION PCIAL.', 'AL. PROYECTO PROGRESISTA']
tdf = {
    '001': ('Ushuaia', [4743,2025,238,911,915,10190,2013,110,541,3031,245,3111],430,1681,45003,28073),
    '002': ('Río Grande', [10613,7039,226,544,1312,2425,4101,617,380,2037,725,2648],496,2182,50329,32667),
    '003': ('Antártida Argentina', [11,34,3,13,9,35,2,1,12,10,6,6],14,3,172,142),
}
rows = []
for sec, (sn, vs, bla, nul, el, pos) in tdf.items():
    assert sum(vs) == pos
    for i, (name, v) in enumerate(zip(names, vs)):
        rows.append(dict(distrito_id='24', distrito_nombre='Tierra del Fuego', seccion_id=sec,
                         seccion_nombre=sn, agrupacion_id='T%02d'%i, agrupacion_nombre=name, votos_tipo='POSITIVO', v=v,
                         cargo_nombre='DIPUTADOS NACIONALES'))
    for typ, v in [('BLANCO',bla),('NULO',nul)]:
        rows.append(dict(distrito_id='24', distrito_nombre='Tierra del Fuego', seccion_id=sec,
                         seccion_nombre=sn, agrupacion_id='', agrupacion_nombre='', votos_tipo=typ, v=v,
                         cargo_nombre='DIPUTADOS NACIONALES'))
for n, frag in [('JUSTICIALISTA','kirchnerismo'),('UNION CIVICA RADICAL','Acuerdo Cívico'),
                ('FEDERAL FUEGUINO','Peronismo Federal'),('AL. PROYECTO PROGRESISTA','Acuerdo Cívico'),
                ('PROYECTO SUR','Movimiento Proyecto Sur')]:
    mapping[('Tierra del Fuego',n)] = find(frag)
votes = pd.concat([votes, pd.DataFrame(rows)], ignore_index=True)

D2P = dict(zip(votes.distrito_id, votes.distrito_nombre))
D2P['01'] = 'Capital Federal'
source = ast.parse((ROOT/'mapa2013/build_2013.py').read_text(encoding='utf8'))
# Se reutilizan únicamente las equivalencias geométricas y los nombres de barrios.
from names import norm
ns = {'norm':norm}
for node in source.body:
    if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('EALIAS','NICE','BARRIOS_COMUNA') for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'),ns)
EALIAS, NICE, BARRIOS_COMUNA = (ns[k] for k in ('EALIAS','NICE','BARRIOS_COMUNA'))
for p, pairs in {
 'Buenos Aires': [('Las Heras','General Las Heras'),('Gonzales Chaves','Adolfo Gonzales Chaves'),('Juárez','Benito Juarez'),('Matanza','La Matanza'),('Nueve de Julio','9 de Julio'),('Veinticinco de Mayo','25 de Mayo'),('F. Ameghino','Florentino Ameghino'),('J. C. Paz','Jose C. Paz')],
 'Córdoba': [('Roque Sáenz Peña','Presidente Roque Saenz Peña')],
 'Chaco': [('Primero de Mayo','1 de Mayo'),('Pcia. de la Plaza','Presidencia de la Plaza'),('Lib. Gral. San Martín','Libertador General San Martin'),('Mayor L. J. Fontana','Mayor Luis J. Fontana'),('Fray J. Sta. María de Oro','Fray Justo Santa Maria de Oro')],
 'Chubut': [('F. Ameguino','Florentino Ameghino')],
 'Jujuy': [('General Belgrano','Dr. Manuel Belgrano')],
 'La Rioja': [('Felipe Varela','Coronel Felipe Varela'),('Angel Vicente Peñaloza','General Angel V. Peñaloza'),('Juan Facundo Quiroga','General Juan F. Quiroga')],
 'Mendoza': [('Luján','Lujan de Cuyo')],
 'Misiones': [('Concepción de la Sierra','Concepcion'),('L. General San Martín','Libertador General San Martin')],
 'Río Negro': [('Nueve de Julio','9 de Julio')],
 'Salta': [('San Martín','General Jose de San Martin')],
 'San Juan': [('Nueve de Julio','9 de Julio')],
 'San Luis': [('Capital','La Capital'),('Pringles','Coronel Pringles'),('Pedernera','General Pedernera'),('San Martín','Libertador General San Martin')],
 'Santa Fe': [('Nueve de Julio','9 de Julio')],
 'Santiago del Estero': [('Matara','Juan F. Ibarra'),('Taboada','General Taboada')],
 'Tucumán': [('Alberdi','Juan B. Alberdi')],
}.items():
    for a,b in pairs: EALIAS[(p,norm(a))] = norm(b)
SUBSEC_MERGE = {}

style = {
    'ACyS': ('Acuerdo Cívico','Acuerdo Cívico y Social','UCR, PS, ARI y aliados','#e10019'),
    'FPV': ('kirchnerismo','Frente para la Victoria','PJ y aliados','#50ade6'),
    'PRO': ('Propuesta Republicana','Unión PRO','PRO y aliados','#f4ce00'),
    'PF': ('Peronismo Federal','Peronismo Federal','y aliados','#1aff98'),
    'SUR': ('Movimiento Proyecto Sur','Proyecto Sur','Movimiento Proyecto Sur','#389b00'),
    'FRC': ('Frente Renovador de la Concordia','Frente Renovador de la Concordia','Misiones','#294593'),
    'MPN': ('Movimiento Popular Neuquino','Movimiento Popular Neuquino','Neuquén','#00708b'),
    'UdN': ('Unión de los Neuquinos','Unión de los Neuquinos','Frente Grande · Neuquén','#f59e0b'),
    'NE': ('Nuevo Encuentro','Nuevo Encuentro','Buenos Aires','#008fc3'),
}
group_code = {find(v[0]):k for k,v in style.items()}
# Se conserva el bloque de todas las listas en el control, aunque no gane ninguna unidad.
votes['grupo_wiki'] = [mapping.get((p,n),'Sin agrupar') for p,n in zip(votes.distrito_nombre,votes.agrupacion_nombre)]
w = votes[votes.votos_tipo=='POSITIVO'].groupby(['distrito_id','seccion_id','grupo_wiki']).v.sum()
winners = Counter(k[2] for k in w.groupby(level=[0,1]).idxmax())
assert not (set(winners)-set(group_code)), winners
BLOCS = tuple(style)
CAND = {k:dict(n=v[1], sub=v[2], base=v[3], logo=k) for k,v in style.items()}
# Paleta del mapa presidencial de 2007 (FPV, PRO) y Peronismo Federal en el verde menta de Rodríguez Saá (20-oct-2026).
CAND.update(P_BLA=dict(n='Votos en blanco',base='#b5b5b5'),P_NUL=dict(n='Votos nulos e impugnados',base='#8a8a8a'))
LIST2BLOC = {(d,a):group_code[grp.iloc[0].grupo_wiki] for (d,a),grp in votes[votes.votos_tipo=='POSITIVO'].groupby(['distrito_id','agrupacion_id']) if grp.iloc[0].grupo_wiki in group_code}
MESAS = {}
for (d,s), g in mesas.groupby(['distrito_id','seccion_id']):
    MESAS[(d,s)] = dict(n=len(g),ok=len(g),e_tot=int(g.mesa_electores.sum()),e_ok=int(g.mesa_electores.sum()))
for sec, rec in tdf.items():
    MESAS[('24',sec)] = dict(n=0,ok=0,e_tot=rec[4],e_ok=rec[4])
AG = votes, mesas

out = ROOT/'mapa2009'
audit = votes[votes.votos_tipo=='POSITIVO'].groupby(['distrito_nombre','agrupacion_id','agrupacion_nombre','grupo_wiki']).v.sum().reset_index()
audit.to_csv(out/'mapeo_listas_2009.csv',index=False,encoding='utf-8-sig')
control = votes[votes.votos_tipo=='POSITIVO'].groupby('grupo_wiki').v.sum().rename('base').to_frame()
control['wikipedia'] = [lookup.get(g,{}).get('total') for g in control.index]
control['diferencia'] = control['base']-control['wikipedia']
control.to_csv(out/'control_bloques_2009.csv',encoding='utf-8-sig')
print('Ganadores por seccion (antes de unir Antártida a Ushuaia):',dict(winners))
