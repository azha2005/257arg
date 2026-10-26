"""Partido de Cantón -> fila de la tabla de Wikipedia -> bloque del atlas.

fila(anio, provincia, partido_canton) devuelve el nombre de la fila del artículo (provincial en 1962/65, nacional en 1958);
BLOQUE[anio][fila] da el bloque (los que no están van a «otros»)."""
import re

def _n(s):
    s = s.lower().replace('partido ', '').strip()
    return re.sub(r'\s+', ' ', s)

# --- 1958: filas de la tabla nacional ----------------------------------------------------------
R58 = [
    (r'^uni[oó]n c[ií]vica radical intransigente$', 'UCRI'),
    (r'roja y blanca|rojo y blanco', 'UCRI Rojo y Blanco'),
    (r'intransigente y renovador', 'UCRI y Renovación'),
    (r'^uni[oó]n c[ií]vica radical del pueblo$', 'UCRP'),
    (r'^dem[oó]crata cristiano$', 'PDC'),
    (r'^socialista$', 'PS'),
    (r'^dem[oó]crata progresista$', 'PDP'),
    (r'alianza chaque', 'Alianza Chaqueña'),
    (r'^dem[oó]crata conservador popular$', 'PDCP'),
    (r'^uni[oó]n popular$', 'Unión Popular'),
    (r'^uni[oó]n popular populista$', 'Unión Popular Populista'),
    (r'^populista$', 'Partido Populista'),
    (r'^dem[oó]crata$', 'Partido Demócrata'),
    (r'^conservador$', 'Partido Conservador'),
    (r'^dem[oó]crata conservador$', 'Partido Demócrata Conservador'),
    (r'dem[oó]crata conservador de catamarca', 'Partido Demócrata Conservador'),
    (r'^uni[oó]n provincial$', 'Unión Provincial'),
    (r'formoseño', 'Partido Demócrata Formoseño'),
    (r'^dem[oó]crata liberal$', 'Partido Demócrata Liberal'),
    (r'^c[ií]vico independiente$', 'Partido Cívico Independiente'),
    (r'bloquista tradicional', 'UCR Bloquista Tradicional'),
    (r'bloquista convenci', 'UCR Bloquista - Conservador Popular'),
    (r'^laborista$', 'Partido Laborista'),
    (r'^laborista federal popular$', 'Partido Laborista Federal Popular'),
    (r'^laborista nacional$', 'Partido Laborista Nacional'),
    (r'^laborista federal agrario$', 'Partido Laborista Federal Agrario'),
]
# conservadores: filas que Wikipedia enlaza al Partido Demócrata Nacional / Federación Nacional de Partidos de Centro (mismo color)
CONS58 = {'Partido Demócrata', 'Partido Conservador', 'Partido Demócrata Conservador', 'Unión Provincial', 'Partido Demócrata Formoseño', 'Partido Demócrata Liberal'}
BLOQUE = {
    1958: dict({'UCRI': 'UCRI', 'UCRP': 'UCRP', 'Partido Populista': 'NPE', 'UCRI Rojo y Blanco': 'URB'}, **{f: 'CON' for f in CONS58}),
}

def fila58(prov, p):
    n = _n(p)
    for rx, f in R58:
        if re.search(rx, n): return f
    return 'otro: ' + p

# --- 1962 y 1965: filas de las tablas provinciales -----------------------------------------------
FJ62 = {'Unión Popular', 'Partido Laborista', 'Partido Tres Banderas', 'Partido Blanco', 'Movimiento Cívico Bandera Popular', 'Partido del Pueblo',
        'Unión Cívica Radical Bloquista', 'Partido Laborista Nacional', 'Movimiento Federal Democrático', 'Movimiento Popular Neuquino',
        'Partido Provincial del Chubut', 'Partido Populista', 'Unión Popular Demócrata Cristiana', 'Unión Cívica Movimiento Nacional y Popular',
        'Movimiento Popular Argentino', 'Partido Laborista Federal Agrario', 'Movimiento Unidad y Progreso'}
UCRP62 = {'Unión Cívica Radical del Pueblo', 'Movimiento Radical Popular', 'Unión Cívica Radical Intransigente Lista Verde'}
FNPC62 = {'Partido Demócrata', 'Unión Conservadora', 'Partido Liberal de Corrientes', 'Partido Autonomista de Corrientes', 'Partido Conservador Popular',
          'Partido Demócrata Conservador', 'Partido Demócrata Unido', 'Unión Provincial', 'Concentración Democrática', 'Partido Demócrata Conservador Popular',
          'Partido Conservador', 'Partido Demócrata Popular', 'Partido Autonomista de Santiago del Estero', 'Partido Demócrata Nacional',
          'Partido Demócrata de Río Negro'}
BLOQUE[1962] = dict({f: 'FJ' for f in FJ62}, **{f: 'UCRP' for f in UCRP62}, **{f: 'FNPC' for f in FNPC62},
                    **{'Unión Cívica Radical Intransigente': 'UCRI', 'Partido Socialista Democrático': 'PSD', 'Partido Demócrata Progresista': 'PDP'})
MPP65 = {'Partido Tres Banderas (PTB)', 'Acción Provinciana (AP)', 'Movimiento Popular Mendocino (MPM)', 'Partido Blanco', 'Partido de la Justicia Social',
         'Partido Laborista (PL)', 'Acción Popular Sanluiseña (APSL)', 'Movimiento Popular Neuquino (MPN)', 'Partido Provincial del Chubut (PPCh)'}
BLOQUE[1965] = dict({f: 'MPP' for f in MPP65},
                    **{'Unión Popular (UP)': 'UP', 'Unión Cívica Radical del Pueblo (UCRP)': 'UCRP', 'Movimiento de Integración y Desarrollo (MID)': 'MID',
                       'Unión Cívica Radical Intransigente (UCRI)': 'UCRI', 'Partido Demócrata Progresista (PDP)': 'PDP',
                       'Unión Cívica Radical Bloquista (UCRB)': 'UCRB', 'Movimiento Línea Las Flores-Luján': 'MFL', 'Partido Unidad Nacional': 'PUN'})
# FNPC 1965: filas con (FNPC-...) más el Pacto Autonomista-Liberal y el Frente Popular Correntino (dentro del total de la FNPC en la tabla nacional)
FNPC65_EXTRA = {'Partido Liberal de Corrientes (PLCo)', 'Partido Autonomista de Corrientes (PACo)', 'Partido Colorado'}

def bloque(anio, prov, f):
    if anio == 1965:
        if '(FNPC' in f or f in FNPC65_EXTRA: return 'FNPC'
        if prov == 'Corrientes' and f in ('Movimiento de Integración y Desarrollo (MID)', 'Partido Demócrata Progresista (PDP)'): return 'FNPC'   # Frente Popular Correntino
    return BLOQUE[anio].get(f)

# --- emparejamiento automático por nombre dentro de la provincia (1962/65) ---------------------------
import unicodedata
def _k(s):
    s = unicodedata.normalize('NFKD', s); s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'\b(partido|el|la|de|del|y|los)\b', ' ', s)
    return re.sub(r'[^a-z]', '', s)

OVR = {   # (anio, provincia, partido Cantón) -> fila de Wikipedia
    (1962, 'Chaco', 'Unión Cívica Radical del Pueblo (Lista Verde)'): 'Unión Cívica Radical Intransigente Lista Verde',
    (1962, 'Corrientes', 'Liberal'): 'Partido Liberal de Corrientes',
    (1962, 'Corrientes', 'Demócrata Autonomista Conservador Popular'): 'Partido Autonomista de Corrientes',
    (1962, 'Neuquén', 'Unión Cívica Intransigente'): 'Unión Cívica Radical Intransigente',
    (1962, 'Santiago del Estero', '*'): None,
    (1962, 'Capital Federal', 'Unión Cívica Principista'): 'Unión Cívica Radical Principista',
    (1962, 'Capital Federal', 'Unión Popular Demócrata Cristiano'): 'Unión Popular Demócrata Cristiana',
    (1962, 'Capital Federal', 'Unión Cívica'): 'Unión Cívica',
    (1962, 'Buenos Aires', 'Socialismo Argentino de Vanguardia'): 'Partido Socialista Argentino de Vanguardia',
    (1962, 'Chaco', 'Socialismo Argentino Federación Chaqueña'): 'Partido Socialista Argentino Federación Chaqueña',
    (1962, 'Chubut', 'Socialismo Argentino Federación Chaqueña'): 'Partido Socialista Argentino (Casa del Pueblo)',
    (1962, 'Jujuy', 'Movimiento Provincial Recuperación Radical'): 'Movimiento Recuperación Radical',
    (1962, 'San Juan', 'Unión Cívica Cruzada Renovadora'): 'Unión Cívica Radical Cruzada Renovadora',
    (1962, 'Santa Fe', 'Socialismo Frente de los Trabajadores'): 'Partido Socialista Frente de los Trabajadores',
    (1962, 'Santa Fe', 'Unión Cívica Movimiento Radical Nacional y Popular'): 'Unión Cívica Movimiento Nacional y Popular',
    (1962, 'Mendoza', 'Blanco'): 'Partido Blanco', (1962, 'Tucumán', 'Blanco'): 'Partido Blanco',
    (1962, 'Río Negro', 'Blanco de Río Negro'): 'Partido Blanco', (1962, 'Río Negro', 'Demócrata'): 'Partido Demócrata de Río Negro',
    (1965, 'Río Negro', 'Blanco de Río Negro'): 'Partido Blanco', (1965, 'San Juan', 'Blanco'): 'Partido Blanco',
    (1965, 'Santa Fe', 'Blanco de Santa Fé'): 'Partido Blanco', (1965, 'Tucumán', 'Blanco'): 'Partido Blanco',
    (1965, 'Santa Fe', 'Demócrata'): 'Partido Demócrata Conservador (FNPC-PADECO)',
    (1965, 'Neuquén', 'Movimiento Popular de Neuquén'): 'Movimiento Popular Neuquino (MPN)',
    (1965, 'San Juan', 'Unión Cívica Radical Renovadora'): 'Unión Cívica Radical Cruzada Renovadora',
    (1965, 'Capital Federal', 'Alianza de la Juventud Socialista'): 'Alianza de la Justicia Social',
    (1965, 'Corrientes', 'Liberal'): 'Partido Liberal de Corrientes (PLCo)',
    (1965, 'Corrientes', 'Autonomista'): 'Partido Autonomista de Corrientes (PACo)',
    (1965, 'Corrientes', 'Colorado'): 'Partido Colorado',
    (1965, 'Buenos Aires', 'Movimiento Flores-Luján'): 'Movimiento Línea Las Flores-Luján',
    (1965, 'Santa Cruz', 'Unidad Nacional'): 'Partido Unidad Nacional',
    (1965, 'Capital Federal', 'Reconstrucción Nacional'): 'Partido de la Reconstrucción Nacional',
    (1965, 'Buenos Aires', 'Partido Reconstrucción Argentina'): 'Partido de la Reconstrucción Argentina (PRAR)',
    (1965, 'Capital Federal', 'Socialismo Argentino'): 'Partido Socialista Argentino (PSA)',
    (1965, 'Capital Federal', 'Socialismo Democrático'): 'Partido Socialista Democrático (PSD)',
}
# 1965: Catamarca, Formosa, La Rioja y Misiones no tienen tabla en la Wikipedia (el artículo las omite), pero el tomo I de
# Cantón las trae en el resumen nacional de diputados. Se usan las filas equivalentes de las otras provincias.
NOWIKI65 = {
    'Unión Cívica Radical del Pueblo': 'Unión Cívica Radical del Pueblo (UCRP)', 'Unión Popular': 'Unión Popular (UP)',
    'Movimiento de Integración y Desarrollo': 'Movimiento de Integración y Desarrollo (MID)',
    'Unión Cívica Radical Intransigente': 'Unión Cívica Radical Intransigente (UCRI)', 'Demócrata Progresista': 'Partido Demócrata Progresista (PDP)',
    'Demócrata Conservador': 'Partido Demócrata Conservador (FNPC)', 'Demócrata Liberal': 'Partido Demócrata Liberal (FNPC)',
    'De la Justicia Social': 'Partido de la Justicia Social', 'Movimiento de la Justicia Social': 'Partido de la Justicia Social',
    'Blanco de los Trabajadores': 'Partido Blanco', 'Laborista': 'Partido Laborista (PL)',
    'Unión Provincial': 'Unión Provincial (Misiones)',
}
for _p in ('Catamarca', 'Formosa', 'La Rioja', 'Misiones'):
    for _c, _f in NOWIKI65.items(): OVR[(1965, _p, _c)] = _f
BLOQUE[1965]['Unión Provincial (Misiones)'] = 'UPM'

def es_blanco(n): return n.lower().startswith('en blanco') or n.lower() in ('blancos', 'votos en blanco')
def es_nulo(n): return 'anulad' in n.lower() or 'nulos' in n.lower()

def fila(anio, prov, p, wrows):
    if anio == 1958: return fila58(prov, p)
    if (anio, prov, p) in OVR: return OVR[(anio, prov, p)]
    names = [n for n, _ in wrows if not n.startswith('#')]
    kp = _k(p)
    for n in names:
        if _k(n) == kp: return n
    for n in names:   # sigla entre paréntesis o prefijo
        if kp and (_k(n).startswith(kp) or kp.startswith(_k(n))): return n
    return None
