"""Empareja las unidades de Cantón (1958/62/65) con los polígonos de Departamentos_1960."""
import sys, os
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(H, '..', '../mapas/mapa1930'))
import shp
from names import norm
PROV = {'02':'Capital Federal','06':'Buenos Aires','10':'Catamarca','14':'Córdoba','18':'Corrientes','22':'Chaco','26':'Chubut','30':'Entre Ríos','34':'Formosa','38':'Jujuy','42':'La Pampa','46':'La Rioja','50':'Mendoza','54':'Misiones','58':'Neuquén','62':'Río Negro','66':'Salta','70':'San Juan','74':'San Luis','78':'Santa Cruz','82':'Santa Fe','86':'Santiago del Estero','90':'Tucumán','94':'Tierra del Fuego'}
B = os.path.join(H, '..', '../geometria/Base deptos 1869-2022')

def shp_names(f):
    return [(PROV[r['PROV_COD']], r['DEPTO'].strip()) for r in shp.read_dbf(os.path.join(B, f + '.dbf'))]

if __name__ == '__main__':
    from datos import cargar_todo, unidades
    T, _ = cargar_todo()
    S = {(p, norm(n)): n for p, n in shp_names('Departamentos_1960_2026v2') if p != 'Capital Federal'}
    for Y in (1958, 1962, 1965):
        U = unidades(T, Y)
        miss = [(p, u) for (p, u) in U if p != 'Capital Federal' and (p, norm(u)) not in S]
        print(Y, 'sin polígono:', miss)
    used = set()
    for Y in (1958, 1962, 1965):
        used |= {(p, norm(u)) for (p, u) in unidades(T, Y)}
    print('polígonos sin dato en ningún año:', [S[k] + ' (' + k[0] + ')' for k in S if k not in used])
