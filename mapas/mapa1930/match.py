import sys, re, pickle
sys.path.insert(0, '.')
import pandas as pd
from names import norm
PN = {'Cordoba':'Córdoba','Entre Rios':'Entre Ríos','Tucuman':'Tucumán'}
# alias (dato Lupu-Stokes -> nombre del polígono 1914), solo cambios de nombre/ortografía comprobables
ALIAS = {
 ('Buenos Aires','3 de Febrero'):'Caseros', ('Buenos Aires','9 de Julio'):'Nueve de julio',
 ('Buenos Aires','Camapana'):'Campana', ('Buenos Aires','Chascomis'):'Chascomus', ('Buenos Aires','Clavarria'):'Olavarría',
 ('Buenos Aires','Juarez'):'Benito Juarez', ('Buenos Aires','Matanza'):'La Matanza', ('Buenos Aires','Trenque Languen'):'Trenquelauquen',
 ('Catamarca','Valle Viego'):'Valle Viejo', ('Catamarca','Fray Mamerto Esquiu'):'Piedra Blanca',
 ('Corrientes','Mburcuya'):'Mburucuya', ('Entre Ríos','Concepcion del Uruguay'):'Uruguay', ('Entre Ríos','Rosario Tala'):'Tala',
 ('Jujuy','Eumahuaca'):'Humahuaca', ('La Rioja','Governador Gordillo'):'Juarez Celman',
 ('Mendoza','Lujan'):'Lujan de Cuyo', ('Salta','Caldera'):'La Caldera', ('Salta','Candelaria'):'La Candelaria',
 ('San Juan','Ullun'):'Ullum', ('San Luis','Pringles'):'Coronel pringles', ('San Luis','San Martin'):'Libertador Gral.Sn Martín',
 ('Santa Fe','Nueve de Juli'):'9 de Julio',
}
def load_data():
    d = pd.read_csv('../../datos/preparados/lupu_stokes_1912_2003_exportacion.csv')
    p = d[(d.year == 1928) & (d.pres == 1)].copy()
    p['prov'] = p.province.map(lambda s: PN.get(s, s)); return p
