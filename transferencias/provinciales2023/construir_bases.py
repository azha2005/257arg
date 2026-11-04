"""Agrupa las listas sin borrar las identidades provinciales del estudio."""
import json
import pandas as pd
from preparar import HERE, ROOT, norm, nacional
from territorio import agregar

CONFIG = {
    'rn': dict(nombre='Río Negro', distrito='16', fecha='16/04/2023', foco=['JSRN', 'Nos Une Río Negro'],
        nota='JSRN es la lista propia (113.953 votos provinciales). Nos Une Río Negro (40.136), también de Weretilneck, queda separada. No se identifica JSRN con toda la coalición.'),
    'neuquen': dict(nombre='Neuquén', distrito='15', fecha='16/04/2023', foco=['MPN', 'Aliados del MPN', 'Neuquinizate'],
        nota='MPN es la lista 151. Sus colectoras se agrupan como Aliados del MPN; Neuquinizate reúne las listas de Figueroa. Sin abstención: no hay padrón provincial por departamento validado. Cinco circuitos rurales sin correspondencia quedan fuera.'),
    'misiones': dict(nombre='Misiones', distrito='14', fecha='07/05/2023', foco=['Frente Renovador de la Concordia'],
        nota='Definitivo municipal (78 municipios). Se excluyen 495 votos del personal asignado a centros que el Tribunal sólo publica en el total provincial. Sin abstención: los electores municipales incluyen extranjeros.'),
    'salta': dict(nombre='Salta', distrito='17', fecha='14/05/2023', foco=['Gustavo Gobernador', 'Avancemos'],
        nota='Gustavo Gobernador (Sáenz) y Avancemos (Estrada–Zapata) se mantienen separados. El voto a gobernador de Avancemos no permite aislar a Ahora Patria de los demás integrantes.'),
}


def grupos(t, mapping):
    out = pd.DataFrame(index=t.index)
    for c in t:
        if c == 'electores': continue
        k = mapping.get(c, c if c in ['Blanco y nulo','No votó'] else 'Otras listas')
        out[k] = out.get(k,0) + t[c]
    assert abs(out.to_numpy().sum()-t.drop(columns='electores',errors='ignore').to_numpy().sum())<1e-6
    return out


def construir():
    bases = {}
    for key, cfg in CONFIG.items():
        raw = pd.read_pickle(HERE / ('prov_'+key+'.pkl'))
        missing=[]
        if key=='rn':
            t,missing=agregar(key, raw)
            t=grupos(t, {'Alianza Juntos Somos Río Negro':'JSRN','Alianza Nos Une Río Negro':'Nos Une Río Negro',
                'Alianza Cambia Río Negro - Juntos Por El Cambio':'Cambia Río Negro','Alianza Vamos Con Todos':'Vamos con Todos',
                'Primero Río Negro':'Primero Río Negro','Alianza Unidad Para La Victoria':'Unidad para la Victoria',
                'Alianza Frente De Izquierda Y De Trabajadores Unidad (FITU)':'FIT-U'})
        elif key=='salta':
            t=grupos(raw, {'ALIANZA GUSTAVO GOBERNADOR':'Gustavo Gobernador','FRENTE AVANCEMOS':'Avancemos',
                'JUNTOS POR EL CAMBIO':'Juntos por el Cambio','ENTRE TODOS':'Entre Todos',
                'SALTA PARA TODOS - CALIVA GOBERNADORA':'Salta para Todos',
                'FRENTE DE IZQUIERDA MST - PARTIDO OBRERO':'FIT (MST–PO)'})
            t.index=t.index.map(lambda x:norm(x.replace('ROS. DE','ROSARIO DE').replace('SAN MARTIN','GENERAL JOSE DE SAN MARTIN')))
        elif key=='neuquen':
            t,missing=agregar(key,raw)
            mapping={151:'MPN'}
            for k in [914,23,166,915,1,882,863,883]:mapping[k]='Aliados del MPN'
            for k in [191,180,64,192,41,193,190,842,50,901]:mapping[k]='Neuquinizate'
            for k in [673,40,67,72,74]:mapping[k]='Frente de Todos Neuquino'
            mapping.update({674:'FIT-U',675:'Juntos por el Cambio',908:'Cumplir'})
            for c in t:
                if isinstance(c,str):mapping[c]='Blanco y nulo'
            t=grupos(t,mapping)
            assert int(raw.loc[:,[c for c in raw if isinstance(c,int)]].sum().sum())==401015
        else:
            codes=['71','644','653','654','900','901','902','903']
            assert not raw[codes+['blancos','nulos','emitidos']].isna().any().any()
            assert ((raw[codes].sum(1)+raw.blancos+raw.nulos)==raw.emitidos).all()
            raw=raw[codes+['blancos','nulos']]
            t,missing=agregar(key,raw)
            mapping={'900':'Frente Renovador de la Concordia','901':'Juntos por el Cambio','902':'La Fuerza de Todos',
                '903':'Frente Amplio','644':'Integración y Militancia','71':'Partido del Obrero','blancos':'Blanco y nulo','nulos':'Blanco y nulo'}
            t=grupos(t,mapping)
        if (t<0).any().any():raise ValueError(key+' negativos')
        t.to_csv(HERE/('base_'+key+'_gob2023.csv'),encoding='utf-8-sig')
        for election in ['2019p','2023p','2023b']:
            b=nacional(election,cfg['distrito'])
            # Alias de departamentos documentados, nunca coincidencia difusa.
            aliases={'GENERALJOSEDESANMARTIN':'GENERALSANMARTIN','LIBERTADORGENERALSANMARTIN':'LIBERTADORGENERALSANMARTIN','ROSDELAFRONTERA':'ROSARIODELAFRONTERA','VEINTICINCODEMAYO':'25DEMAYO','NUEVEDEJULIO':'9DEJULIO'}
            if key=='rn':aliases['SANANTONIOOESTE']='SANANTONIO'
            if key=='misiones':aliases['CONCEPCIONDELASIERRA']='CONCEPCION'
            if key=='salta':aliases['SANMARTIN']='GENERALSANMARTIN'
            t.index=t.index.map(lambda n:aliases.get(n,n));b.index=b.index.map(lambda n:aliases.get(n,n))
            idx=t.index.intersection(b.index)
            print(key,election,'departamentos',len(idx),'sin cruce',t.index.difference(b.index).tolist(),b.index.difference(t.index).tolist(),flush=True)
            a=t.loc[idx].copy();b=b.loc[idx].copy()
            if 'No votó' not in a:b=b.drop(columns='No votó',errors='ignore')
            if election=='2019p':a,b=b,a
            a=a.loc[:,a.sum()>0];b=b.loc[:,b.sum()>0]
            good=(a.sum(1)>0)&(b.sum(1)>0)
            empty=a.index[~good].tolist()
            # Una unidad nacional sin mesas informadas no representa cero
            # votos ni abstención. Se excluye explícitamente de ambos lados.
            a,b=a.loc[good],b.loc[good]
            governor=b if election=='2019p' else a
            provincial_total=416166 if key=='neuquen' else 695983 if key=='misiones' else float(t.values.sum())
            par=key+'_'+('2019p_gob2023' if election=='2019p' else 'gob2023_'+election)
            cfg2=dict(cfg, id=par, nivel='departamentos', unidades=len(a), base='padrón' if 'No votó' in a else 'votos emitidos',
                origen='Presidente 2019' if election=='2019p' else 'Gobernador '+cfg['fecha'],
                destino='Gobernador '+cfg['fecha'] if election=='2019p' else ('Presidente 22/10/2023' if election=='2023p' else 'Balotaje 19/11/2023'),
                foco_lado='destino' if election=='2019p' else 'origen',pendientes=missing+['Sin votos nacionales informados: '+n for n in empty],
                cobertura_provincial=float(governor.values.sum()/provincial_total),
                cobertura_origen=float(a.to_numpy().sum()/((nacional(election,cfg['distrito']).drop(columns='No votó',errors='ignore') if 'No votó' not in a else nacional(election,cfg['distrito'])).to_numpy().sum())) if election=='2019p' else 1.0)
            bases[par]=(a,b,cfg2)
    pd.to_pickle(bases,HERE/'bases.pkl')
    return bases


if __name__=='__main__':construir()
