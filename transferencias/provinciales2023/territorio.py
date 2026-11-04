"""Correspondencias nominales explícitas para el piloto departamental.

Georef (localidades y asentamientos) aporta los departamentos. Las variantes
de los nombres se registran aquí, sin emparejamiento difuso automático.
Los topónimos que no pueden resolverse quedan fuera y en el control.
"""
import json
import re
import pandas as pd
from preparar import HERE, RAW, georef, norm

ALIASES = {
    'rn': {
        'Bajada Colorada – Naupa Huen':'Naupa Huen',
        'Lonco Vaca – Aguada Guzman':'Aguada Guzmán',
        'Balsa Las Perlas':'Las Perlas',
        'El Foyel – El Manso':'El Manso',
        'Pto. San Antonio Este':'Puerto San Antonio Este',
        'Mro Ramos Mexia':'Ministro Ramos Mexía',
        'Rincon Treneta':'Treneta',
        'Maquinchao Rural – Colan Conhue':'Colán Conhue',
        'Quetrequile':'Quetrequil',
        'Ministro Ramos Mexia Rural – Comico':'Ministro Ramos Mexía',
        'General E.Frias':'Teniente General E. Frías',
        'Vicealmirante O Connor':'Vicealmirante Eduardo O’Connor',
        'Gral Conesa Rural':'General Conesa',
        'Catriel Rural – Peñas Blancas':'Catriel',
    },
    'neuquen': {
        'Bajada Los Molles':'Bajada de los Molles',
        'Butalon Norte - Huinganco Nort':'Butalón Norte',
        'Cajon de Almaza':'Cajón de Almanza',
        'Chacaico Sur':'Chacayco Sur',
        'Chapelco Grande':'Chapelco',
        'Chiuquilihuin':'Chiquilihuin',
        'Colipilli':'Colipilli Abajo',
        'Cura Mallin - Andacollo Sur':'Cura Mallín',
        'Huantraico':'Sierra de Huantraico',
        'Huechulafquen':'Villa Huechulafquen',
        'Lago Lolog - San Martin de los Andes':'San Martín de los Andes',
        'Lago Meliquina':'Villa Lago Meliquina',
        'Ramon Castro':'Ramón M. Castro',
        'Ramon Castro Fuera de Radio':'Ramón M. Castro',
        'Ruca Choroy':'Ruca Choroi',
        'Senillosa Sur-Arroyito':'Senillosa',
        'Taquimilan Arriba':'Taquimilán',
        'Vega Maipu - San Martin de los Andes':'San Martín de los Andes',
        'Villa Angostura - Fuera de Rad':'Villa La Angostura',
        'Villa Curi Leuvu Norte':'Villa Curi Leuvu',
        'Villa Curi Leuvu Sur':'Villa Curi Leuvu',
        'Villa del Puente Picun Leufu N':'Villa Puente Picún Leufú',
        'Villa del Puente Picun Leufu S':'Villa Puente Picún Leufú',
        'Villa Moquehue':'Moquehue',
        'Zapala Sudoeste - Laguna Miran':'Zapala',
    },
    'misiones': {'ltacaruaré':'Itacaruaré','Olegario Víctor Andrade':'Olegario V. Andrade'},
}


def mapa(key):
    prov = {'rn':'rio%20negro','neuquen':'neuquen','misiones':'misiones'}[key]
    g = georef(prov)
    f = RAW / ('asentamientos_' + ('rio' if key=='rn' else key) + '.json')
    if f.exists():
        aux = {}
        for x in json.loads(f.read_text(encoding='utf8'))['asentamientos']:
            aux.setdefault(norm(x['nombre']), set()).add(x['departamento']['nombre'])
        for k, v in aux.items():
            if k not in g and len(v)==1:
                g[k] = list(v)[0]
    alias = {norm(k):norm(v) for k,v in ALIASES[key].items()}
    if key == 'misiones':
        # Digesto provincial y ley XV-17: las fuentes están en LEEME.
        g['FACHINAL']='Capital'
        g['POZOAZUL']='San Pedro'
    if key == 'neuquen':
        # Boletín Oficial de Neuquén, creación de escuela de Pil-Pil.
        g['PILPIL']='Lácar'
    def lookup(n):
        k = norm(n)
        k = alias.get(k,k)
        if k in g: return g[k]
        # Divisiones urbanas del mismo núcleo y etiquetas rurales del visor.
        if key=='neuquen':
            for city in ['BUTA RANQUIL','CENTENARIO','CUTRAL CO','NEUQUEN','PLAZA HUINCUL','PLOTTIER','ZAPALA']:
                if k.startswith(norm(city)) and norm(city) in g:
                    return g[norm(city)]
            k = re.sub(r'FUERADERADIO$', '', k)
            k = re.sub(r'FUERADE$', '', k)
            if k in g: return g[k]
        return None
    return lookup


def agregar(key, t):
    lookup = mapa(key)
    corr = pd.DataFrame({'unidad':t.index, 'departamento':[lookup(n) for n in t.index]})
    corr.to_csv(HERE / ('correspondencias_'+key+'.csv'), index=False, encoding='utf-8-sig')
    missing = corr[corr.departamento.isna()].unidad.tolist()
    print(key, 'SIN DEPARTAMENTO', missing, flush=True)
    t = t.copy()
    t['departamento'] = [lookup(n) for n in t.index]
    out = t.dropna(subset=['departamento']).groupby('departamento').sum(numeric_only=True)
    out.index = out.index.map(norm)
    return out, missing
