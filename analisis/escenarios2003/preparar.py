"""Prepara datos y la página autocontenida. No modifica los Sankey ni los atlas."""
from pathlib import Path
import hashlib
import json
import sys
import subprocess
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'transferencias'))
from estimar import DISTRITOS

# Tabla nacional, no infobox, del wikitext conservado en el proyecto.
CANDIDATOS = [
    ('M', 'Carlos Menem', 'Menem', '0133', 4741200, '#318ce7'),
    ('K', 'Néstor Kirchner', 'Kirchner', '0135', 4313131, '#75aadb'),
    ('L', 'Ricardo López Murphy', 'López Murphy', '0131', 3173584, '#e3b900'),
    ('R', 'Adolfo Rodríguez Saá', 'Rodríguez Saá', '0132', 2736091, '#39bfa0'),
    ('C', 'Elisa Carrió', 'Carrió', '0134', 2723207, '#6fb53e'),
    ('MOREAU', 'Leopoldo Moreau', 'Moreau', '0003', 453373, '#e10019'),
    ('WALSH', 'Patricia Walsh', 'Walsh', '0136', 332703, '#b92546'),
    ('BRAVO', 'Alfredo Bravo', 'Bravo', '0050', 217387, '#c75f48'),
    ('ALTAMIRA', 'Jorge Altamira', 'Altamira', '0014', 139402, '#a60020'),
    ('VENTURINO', 'Enrique Venturino', 'Venturino', '0053', 129782, '#424242'),
    ('SULLINGS', 'Guillermo Sullings', 'Sullings', '0022', 105705, '#d87526'),
    ('ARCAGNI', 'José Carlos Arcagni', 'Arcagni', '0137', 63384, '#27466c'),
    ('MAZZITELLI', 'Mario Mazzitelli', 'Mazzitelli', '0030', 50303, '#c54e68'),
    ('ZAFFORE', 'Carlos Zaffore', 'Zaffore', '0001', 47954, '#577d54'),
    ('HERRERA', 'Manuel Herrera', 'Herrera', '0005', 47755, '#5f778b'),
    ('BREIDE', 'Gustavo Breide Obeid', 'Breide Obeid', '0051', 42461, '#84654f'),
    ('MUSSA', 'Juan Ricardo Mussa', 'Mussa', '0138', 39507, '#ae9627'),
    ('TERAN', 'Ricardo Terán', 'Terán', '0037', 31766, '#567468'),
]
LABEL = {'M':'Menem (Lealtad)', 'K':'Kirchner (FPV)', 'L':'López Murphy (Recrear)',
         'R':'Rodríguez Saá (MNP)', 'C':'Carrió (ARI)'}
GROUPS = [LABEL[k] for k in 'MKLRC'] + ['Otros', 'Blanco y nulo']
KEYS = [c[0] for c in CANDIDATOS]
TARGET = np.array([c[4] for c in CANDIDATOS] + [196563 + 345651], float)
assert sum(TARGET[:-1]) == 19388695
FILES = []


def track(p):
    p = ROOT / p
    FILES.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),
                      sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    return p


def calibrate_columns(F, targets):
    """Preserva el perfil de origen de cada columna; lleva su suma a la base oficial."""
    F = np.asarray(F, float)
    assert np.isfinite(F).all() and (F >= 0).all()
    assert ((F.sum(0) > 0) | (targets == 0)).all()
    factor = np.divide(targets, F.sum(0), out=np.zeros_like(targets), where=F.sum(0)>0)
    return F * factor[None, :]


def expand(F, targets):
    # Los 13 candidatos menores comparten perfil de «Otros»: no se identifica
    # su afinidad individual. Se explicita tanto en la página como en el informe.
    x = np.zeros((len(F), 19))
    x[:, :5] = F[:, :5]
    for j in range(5, 18):
        x[:, j] = F[:, 5] * targets[j] / max(targets[5:18].sum(), 1)
    x[:, 18] = F[:, 6]
    return calibrate_columns(x, targets)


def book_matrix(year, targets):
    if year == 1999:
        # Figura 6.15, p.206: P(origen 1999 | candidato 2003), no la
        # traspuesta de la figura 6.12. Incluye «Otros» residual del receptor.
        F = np.array([[9,37,76,76,78], [89,61,3,4,4], [0,1,21,20,18], [2,1,0,0,0]], float)
        origins = ['Alianza 1999', 'PJ 1999', 'APR 1999', 'Otros de origen 1999']
    else:
        # Figura 6.11, p.201: columnas PJ, Alianza, ARI, derecha,
        # izquierda, provinciales, nulo y blanco de 2001. Porcentajes redondeados.
        B = np.array([[49,34,2,10,6], [28,37,6,27,2], [2,2,22,21,39],
                      [0,0,48,10,29], [6,10,24,17,33], [47,18,21,8,5],
                      [0,15,44,13,20], [9,13,30,12,29]], float)
        w = np.array([4809495,3058569,1078096,674753,1499293,1200118,2261332,1704514])
        F = B * w[:, None]
        origins = ['PJ 2001','Alianza 2001','ARI 2001','Derecha 2001','Izquierda 2001',
                   'Provinciales 2001','Nulo 2001','Blanco 2001']
    F = calibrate_columns(F, targets[:5])
    # El libro no distingue los 13 menores ni blanco/nulo de 2003.
    # Perfil no informativo = mezcla de orígenes de los cinco principales;
    # no se reinterpreta «No estimado» como abstención o partido menor.
    mix = F.sum(1) / F.sum()
    return np.column_stack([F] + [mix * targets[j] for j in range(5,19)]), origins


def main():
    path = track('transferencias/circ_2003p.pkl')
    v, e = pd.read_pickle(path)
    raw = v[v.votos_tipo.eq('POSITIVO')].pivot_table(index='distrito_id', columns='agrupacion_id', values='v', aggfunc='sum', fill_value=0)
    raw = raw.reindex(columns=[c[3] for c in CANDIDATOS], fill_value=0)
    # La geografía es PolAr; cada candidato se calibra al total nacional de
    # la tabla, sin afirmar que sean sus totales provinciales definitivos.
    pos = raw.to_numpy(float) * (TARGET[:18] / raw.sum().to_numpy())[None,:]
    b = v[~v.votos_tipo.eq('POSITIVO')].groupby('distrito_id').v.sum().reindex(raw.index)
    blanks = b.to_numpy() * TARGET[18] / b.sum()
    abst = e.groupby(level=0).sum().reindex(raw.index).to_numpy(float) - v.groupby('distrito_id').v.sum().reindex(raw.index).to_numpy()
    assert (abst >= 0).all()
    abst *= 5550501 / abst.sum()
    baseline = np.column_stack([pos, blanks])
    geo = [dict(id='NAC', name='Total nacional', votes=TARGET.tolist(), abstention=5550501)]
    for n, d in enumerate(raw.index):
        geo.append(dict(id=d, name=DISTRITOS[d], votes=baseline[n].tolist(), abstention=float(abst[n])))

    mp = track('transferencias/1999pe_2003pe/matriz_votos.csv')
    base = pd.read_csv(mp, index_col=0).reindex(columns=GROUPS)
    pp = pd.read_csv(track('transferencias/1999pe_2003pe/por_provincia.csv'), dtype={'distrito':str})
    calvo = pd.read_csv(track('transferencias/1999pe_2003pe/calvo_nacional.csv'), index_col=0).reindex(columns=GROUPS)
    models = []
    for mid, title in [('principal','Sankey del proyecto'),('calvo','Variante Calvo del proyecto'),
                       ('libro1999','Libro: origen presidencial 1999'),('libro2001','Libro: origen legislativo 2001')]:
        joints = []
        for g in geo:
            targets = np.array(g['votes'])
            if mid == 'principal':
                F = base if g['id']=='NAC' else pp[pp.distrito.eq(g['id'])].pivot(index='origen',columns='destino',values='votos').reindex(index=base.index,columns=GROUPS,fill_value=0).fillna(0)
                if np.any(F.sum(0).to_numpy() <= 0):
                    raise ValueError(f'Columna sin soporte {g["id"]}')
                J = expand(F.to_numpy(), targets)
                origins = list(base.index)
            elif mid == 'calvo':
                J = expand(calvo.to_numpy(), targets)
                origins = list(calvo.index)
            else:
                # Se usan los perfiles nacionales del libro, sin inventar
                # matrices provinciales propias para él.
                J, origins = book_matrix(int(mid[5:]), TARGET)
                J = calibrate_columns(J, targets)
            joints.append(np.round(J, 8).tolist())
        models.append(dict(id=mid, name=title, origins=origins, joints=joints))
    retrospective = []
    for pair in ['2003p_2005','2003p_2007p','2003p_2009']:
        f = track(f'transferencias/{pair}/matriz_pct.csv')
        t = pd.read_csv(f,index_col=0)
        retrospective.append(dict(pair=pair,columns=list(t.columns),rows=[dict(origin=i,values=r.tolist()) for i,r in t.iterrows()]))
    polls = json.loads((HERE/'encuestas.json').read_text(encoding='utf8'))
    for p in ['datos/fuentes_leg2003_2025/presidenciales/wpres2003.txt','transferencias/1999pe_2003pe/control.json','transferencias/AUDITORIA.md']:
        track(p)
    data = dict(candidates=[dict(id=k,name=name,short=short,code=code,votes=votes,color=color) for k,name,short,code,votes,color in CANDIDATOS],
                geographies=geo, models=models, polls=polls, retrospective=retrospective,manifest=FILES,
                total_positive=19388695, registered=25481410,
                book_path='C:/Users/JC/Downloads/rec8399/libro_calvo_escolar/ilide.info-calvo-y-escolar-2005-la-nueva-politica-de-partidos-en-la-argentina-pr_edd9b61a645ec8b6db8ce73f9bc716a0.pdf')
    (HERE/'datos.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    html = (HERE/'plantilla.html').read_text(encoding='utf8')
    html = html.replace('/*__ENGINE__*/',(HERE/'motor.js').read_text(encoding='utf8'))
    html = html.replace('/*__DATA__*/',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    (HERE/'simulador_2003.html').write_text(html,encoding='utf8')
    print(f'Preparado: {len(CANDIDATOS)} candidatos, {len(geo)} ámbitos, {len(models)} modelos, {len(polls["pares"])} mediciones.')
    subprocess.run([sys.executable,'-X','utf8',str(HERE/'ajustar_local.py')],check=True,cwd=ROOT)


if __name__ == '__main__':
    main()
