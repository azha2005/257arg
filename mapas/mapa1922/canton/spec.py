"""Leyendas de columnas de Canton (tomo II, 1922) por jurisdicción y su agrupación en bloques."""
SPEC = {
 'Buenos Aires':        dict(file='p_BA.txt',  cols=['INS','VOT','UCR','CNC','SOC']),
 'Capital Federal':     dict(file='p_CF.txt',  cols=['INS','VOT','UCR','SOC','PRI','DP','COM','CNC']),
 'Catamarca':           dict(file='p_CAT.txt', cols=['INS','VOT','UCR','SOC','CNC']),
 'Córdoba':             dict(file='p_COR.txt', cols=['INS','VOT','UCR','SOC','DEM']),
 'Corrientes':          dict(file='p_COT.txt', cols=['INS','VOT','UCR','CNC']),
 'Entre Ríos':          dict(file='p_ER.txt',  cols=['INS','VOT','UCR','CNC','INT']),
 'Jujuy':               dict(file='p_JUJ.txt', cols=['INS','VOT','UCR','CNC','BLA']),
 'La Rioja':            dict(file='p_RIO.txt', cols=['INS','VOT','UCR','PRI','UPO']),
 'Salta':               dict(file='p_SAL.txt', cols=['INS','VOT','UCR','UPV','INT']),
 'San Juan':            dict(file='p_SJ.txt',  cols=['INS','VOT','UCR','SOC','BLO','CNC']),
 'San Luis':            dict(file='p_SL.txt',  cols=['INS','VOT','UCR','SOC','ROJ','LIB']),
 'Santa Fe':            dict(file='p_SF.txt',  cols=['INS','VOT','UCR','SOC','DP']),
 'Tucumán':             dict(file='p_TUC.txt', cols=['INS','VOT','UTU','SOC','OPO','LIB']),
}
PARTY = {
 'UCR': 'Unión Cívica Radical', 'CNC': 'Concentración Nacional', 'CON': 'Conservador (Prov. de Buenos Aires)', 'SOC': 'Socialista',
 'PRI': 'UCR Principista', 'DP': 'Demócrata Progresista', 'COM': 'Comunista', 'DEM': 'Demócrata (Córdoba)',
 'INT': 'UCR Intransigente', 'UPV': 'Unión Provincial (Salta)', 'UPO': 'Unión Popular (La Rioja)', 'BLO': 'UCR Bloquista',
 'ROJ': 'UCR Roja (San Luis)', 'UTU': 'UCR de Tucumán (rotulada «Unión Cívica Radical» por Cantón)', 'LAU': 'Radicales disidentes (Laurencena)', 'LIB': 'Liberales', 'OPO': 'Radicales opositores (Tucumán) = UCR de Alvear', 'BLA': 'En blanco',
}
# bloques para el mapa (los de la Wikipedia: Alvear / Piñero / Repetto / Laurencena / Ibarguren)
BLOC = {'UCR': 'UCR', 'OPO': 'UCR', 'UTU': 'DIS', 'LAU': 'DIS', 'CNC': 'CON', 'UPV': 'CON', 'UPO': 'CON', 'DEM': 'CON', 'LIB': 'CON',
        'SOC': 'SOC', 'PRI': 'DIS', 'BLO': 'DIS', 'ROJ': 'DIS', 'INT': 'DIS',
        'DP': 'PDP'}    # 'COM' y 'BLA' quedan fuera de los bloques
