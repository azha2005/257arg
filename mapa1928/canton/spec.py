"""Leyendas de columnas de Canton (tomo II, 1928) por jurisdicción y su agrupación."""
# código de partido por columna (1-based)
SPEC = {
 'Buenos Aires':        dict(file='p_BA.txt',  cols=['INS','VOT','UCR','ANT','SOC','FME','CON','BLA']),
 'Capital Federal':     dict(file='p_CF.txt',  cols=['INS','VOT','UCR','ANT','SOC','COM','COM','COM']),
 'Catamarca':           dict(file='p_CAT.txt', cols=['INS','VOT','UCR','SOC','FME','BLA','VAR']),
 'Córdoba':             dict(file='p_COR.txt', cols=['INS','VOT','UCR','SOC','COM','FME']),
 'Corrientes':          dict(file='p_COT.txt', cols=['INS','VOT','UCR','ANT','SOC','BLA']),
 'Entre Ríos':          dict(file='p_ER.txt',  cols=['INS','VOT','UCR','SOC','FME','BLA','VAR']),
 'Jujuy':               dict(file='p_JUJ.txt', cols=['INS','VOT','UCR','ANT','SOC','BLA','VAR']),
 'La Rioja':            dict(file='p_RIO.txt', cols=['INS','VOT','UCR','ANT','SOC','BLA','VAR']),
 'Mendoza':             dict(file='p_MZA.txt', cols=['INS','VOT','UCR','SOC','COM','LIB','LEN']),
 'Salta':               dict(file='p_SAL.txt', cols=['INS','VOT','UCR','ANT','BLA']),
 'San Juan':            dict(file='p_SJ.txt',  cols=['INS','VOT','SOC','BLA','VAR','BLO','FER','FER']),
 'San Luis':            dict(file='p_SL.txt',  cols=['INS','VOT','UCR','SOC','BLA','LIB']),
 'Santa Fe':            dict(file='p_SF.txt',  cols=['INS','VOT','UCR','UNI','DP','VAR']),
 'Santiago del Estero': dict(file='p_SGO.txt', cols=['INS','VOT','UCR','ANT','SOC','BLA']),
 'Tucumán':             dict(file='p_TUC.txt', cols=['INS','VOT','UCR','SOC','COM','FME','BLA','LIB']),
}
PARTY = {
 'UCR': 'Unión Cívica Radical', 'ANT': 'UCR Antipersonalista', 'UNI': 'UCR Unificada', 'SOC': 'Socialista',
 'FME': 'Frente Único Melo–Gallo', 'CON': 'Conservador', 'LIB': 'Liberal', 'DP': 'Demócrata Progresista',
 'LEN': 'UCR Lencinista', 'BLO': 'UCR Bloquista', 'FER': 'Listas «Ferrocarril» (San Juan)',
 'COM': 'Comunistas', 'VAR': 'Varios', 'BLA': 'En blanco',
}
# bloques para el mapa: las formulas de la Wikipedia («Elecciones presidenciales de Argentina de 1928», tabla de resultados).
# Melo–Gallo = Confederacion de las Derechas (antipersonalistas, Frente Unico, conservadores, unificados, lencinistas, bloquistas, liberales);
# Matienzo–Carles = listas «UCR Ferrocarril a Jachal / a Calingasta» (San Juan); el PDP no presento formula.
BLOC = {'UCR': 'YRI', 'ANT': 'MEL', 'UNI': 'MEL', 'FME': 'MEL', 'CON': 'MEL', 'LIB': 'MEL', 'LEN': 'MEL', 'BLO': 'MEL',
        'SOC': 'SOC', 'FER': 'MAT', 'DP': 'PDP',
        'COM': 'OTR', 'VAR': 'OTR'}   # 'BLA' = en blanco (aparte)
