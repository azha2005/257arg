"""Leyendas de columnas de Cantón (tomo II, diputados 1930) por jurisdicción y su agrupación."""
SPEC = {
 'Buenos Aires':    dict(file='p_BA.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'COM', 'COM', 'CON']),
 'Catamarca':       dict(file='p_CAT.txt', cols=['INS', 'VOT', 'FIG', 'UCS'], ucr=['FIG', 'UCS']),
 'Córdoba':         dict(file='p_COR.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'COM', 'PDC']),
 'Corrientes':      dict(file='p_COT.txt', cols=['INS', 'VOT', 'UCR', 'LIB', 'AUT']),
 'Entre Ríos':      dict(file='p_ER.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'ANT']),
 'Jujuy':           dict(file='p_JUJ.txt', cols=['INS', 'VOT', 'UCR', 'UJP'], ucr=['UCR', 'UJP']),
 'La Rioja':        dict(file='p_RIO.txt', cols=['INS', 'VOT', 'UCR', 'UPI']),
 'Mendoza':         dict(file='p_MZA.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'PSI', 'LEN', 'ROJ', 'LIB'], ucr=['UCR', 'LEN', 'ROJ']),
 'Salta':           dict(file='p_SAL.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'UPR']),
 'San Juan':        dict(file='p_SJ.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'BLO'], ucr=['UCR', 'BLO']),
 'Santa Fe':        dict(file='p_SF.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'COM', 'PDP', 'CAB', 'UNI'], ucr=['UCR', 'CAB', 'UNI']),
 'Santiago del Estero': dict(file='p_SDE.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'UNI', 'COR'], ucr=['UCR', 'UNI', 'COR']),
 'Tucumán':         dict(file='p_TUC.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'PSI', 'COM', 'UOP', 'LIB', 'DPB', 'AGR', 'UTU'], ucr=['UCR', 'UOP', 'UTU']),
 'Capital Federal': dict(file='p_CF.txt', cols=['INS', 'VOT', 'UCR', 'SOC', 'PSI', 'VAR', 'VAR', 'COM', 'COM']),
}
PARTY = {
 'UCR': 'Unión Cívica Radical', 'SOC': 'Socialista', 'PSI': 'Socialista Independiente', 'CON': 'Conservador',
 'UCS': 'UCR Situacionista', 'LIB': 'Liberal', 'AUT': 'Coalición Autonomista', 'ANT': 'UCR Antipersonalista', 'UJP': 'UCR Disidente (J. y P.)', 'FIG': 'UCR Figueroísta', 'PDC': 'Partido Demócrata de Córdoba', 'UPI': 'UCR Principista', 'LEN': 'UCR Lencinista', 'ROJ': 'Radical Rojo', 'UPR': 'Unión Provincial', 'BLO': 'UCR Bloquista', 'PDP': 'Demócrata Progresista', 'CAB': 'UCR Caballero', 'UNI': 'UCR Unificada', 'COR': 'UCR Corvalanista', 'UOP': 'UCR Opositora', 'DPB': 'Defensa Provincial Bandera Blanca', 'AGR': 'Agrario', 'UTU': 'UCR (Tucumán)', 'COM': 'Comunistas', 'VAR': 'Varios', 'BLA': 'En blanco',
}
# Bloques del atlas, como los agrupa Wikipedia («Elecciones legislativas de Argentina de 1930»):
# UCR = alianza UCR (UCR + Situacionista de Catamarca); CD = Confederación de las Derechas; RAN = radicalismo antipersonalista
# (incluye la columna «UCR» de Catamarca, que Wikipedia identifica como UCR Figueroísta, y la J. y P. de Jujuy = UCR Disidente);
# PS, PSI, PDP, LEN, BLO van aparte; el resto, a «otros».
BLOC = {'UCR': 'UCR', 'UCS': 'UCR',
        'CON': 'CD', 'PDC': 'CD', 'LIB': 'CD', 'AUT': 'CD', 'UPR': 'CD',
        'UNI': 'RAN', 'ANT': 'RAN', 'CAB': 'RAN', 'UOP': 'RAN', 'COR': 'RAN', 'FIG': 'RAN', 'UPI': 'RAN', 'UJP': 'RAN', 'ROJ': 'RAN', 'UTU': 'RAN',
        'SOC': 'PS', 'PSI': 'PSI', 'PDP': 'PDP', 'LEN': 'LEN', 'BLO': 'BLO',
        'DPB': 'OTR', 'AGR': 'OTR', 'COM': 'OTR', 'VAR': 'OTR'}
