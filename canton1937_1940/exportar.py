from pathlib import Path
from collections import defaultdict, Counter
import csv, hashlib, json

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
BASE = ['Inscriptos', 'Votantes']
UCR = 'Unión Cívica Radical'
DN = 'Demócrata Nacional'
SOC = 'Socialista'
CP = 'Conjunción Peronista'
UD = 'Unión Democrática'
LAB = 'Laborista'
BL = 'En Blanco'
OBS = 'Observados y/o anulados'
CIRC = dict(zip(['Balvanera Norte','Balvanera Oeste','Balvanera Sud','Belgrano','Concepción','Flores','Las Heras','Monserrat','Palermo','Pilar','San Bernardo','San Carlos Norte','San Carlos Sud','San Cristóbal Norte','San Cristóbal Sud','San Juan Evangelista','San Nicolás','Santa Lucía','Socorro','Vélez Sarsfield'],[11,9,10,16,12,5,18,13,17,19,15,7,6,8,2,4,14,3,20,1]))
META = {
    142: (1937, 'Capital Federal', 143, [UCR, 'Concordancia', SOC, UCR+' (Molinari)']),
    143: (1937, 'Córdoba', 144, [UCR, SOC, DN, UCR+' (Junta Renovadora Nacional)', BL, OBS]),
    144: (1937, 'La Rioja', 145, [UCR, 'Concordancia', BL, OBS]),
    145: (1937, 'Tucumán', 146, [UCR, 'Concordancia', SOC, 'Defensa Provincial', BL, OBS]),
    147: (1940, 'Capital Federal', 149, ['Concordancia', SOC, UCR+' Capital', 'Concentración Obrera', 'Partido Radical', 'Agrupación Defensiva', 'Social Independiente', 'Radical Unificado', 'Conservador']),
    148: (1940, 'Córdoba', 150, [UCR, SOC, DN, 'Blanco']),
    149: (1940, 'Entre Ríos', 151, [UCR, DN, SOC, 'Blanco']),
    150: (1940, 'Santa Fe', 152, [UCR, 'Partido Socialista', UCR+' Santa Fe', 'En Blanco']),
    151: (1940, 'Tucumán', 153, [UCR, DN, UCR+' Frente Popular', SOC, 'Agrario', 'Blanco y Anulados']),
    153: (1946, 'Capital Federal', 157, [CP, UD]),
    154: (1946, 'Buenos Aires', 158, [CP, UD, DN]),
    155: (1946, 'Buenos Aires', 159, [CP, UD, DN]),
    156: (1946, 'Buenos Aires', 160, [CP, UD, DN]),
    157: (1946, 'Buenos Aires', 161, [CP, UD, DN]),
    158: (1946, 'Catamarca', 162, [LAB, UCR+' (Junta Renovadora)', UCR+' (Comité Nacional)']),
    159: (1946, 'Córdoba', 163, [CP, UD]),
    160: (1946, 'Corrientes', 164, [CP, UD]),
    161: (1946, 'Entre Ríos', 165, [CP, DN, UCR+' (Comité Nacional)']),
    162: (1946, 'Jujuy', 166, [CP, UD]),
    163: (1946, 'La Rioja', 167, [CP, UD]),
    164: (1946, 'Mendoza', 168, [CP, UD, UCR+' Lencinista']),
    165: (1946, 'Salta', 169, [CP, UCR+' (Comité Nacional)']),
    166: (1946, 'San Juan', 170, [CP, UD, UCR+' Bloquista']),
    167: (1946, 'San Luis', 171, [UD, LAB]),
    168: (1946, 'Santa Fe', 172, [CP, UD]),
    169: (1946, 'Santiago del Estero', 173, [UD, LAB, UCR+' (Santiago del Estero)']),
    170: (1946, 'Tucumán', 174, [UD, 'Partido Laborista', UCR+' Irigoyenista', 'Partido Laborista de Tucumán']),
}


def load():
    pages = {}
    for folder in [ROOT, PROJECT/'canton1946']:
        for line in (folder/'manual.txt').read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'): continue
            p, name, literals = line.split('|')
            p = int(p)
            year, district, printed, labels = META[p]
            labels = BASE+labels
            vals = literals.split()
            assert len(vals) == len(labels), (p,name,len(vals),len(labels))
            page = pages.setdefault(p, {'anio':year, 'tomo':'II', 'pagina_pdf':p, 'pagina_libro':printed, 'provincia':district, 'eleccion':'Diputados nacionales' if year==1940 else 'Electores de Presidente y Vice', 'categoria':'varones solamente', 'columnas':dict(enumerate(labels,1)), 'filas':[]})
            assert not any(r['unidad']==name for r in page['filas']), (p,name)
            page['filas'].append({'unidad':name, 'circunscripcion':CIRC.get(name) if district=='Capital Federal' else None, 'valores':{c:int(v) if v.isdigit() else None for c,v in enumerate(vals,1)}, 'marcas':{c:v for c,v in enumerate(vals,1) if not v.isdigit()}, 'metodo':'Transcripción visual del escaneo'})
    return [pages[p] for p in sorted(pages)]


def main():
    pages = load()
    source = PROJECT/'raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf'
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    for year in [1937,1940,1946]:
        folder = PROJECT/f'canton{year}' if year==1946 else ROOT/f'{year}'
        folder.mkdir(exist_ok=True)
        subset = [p for p in pages if p['anio']==year]
        meta = {'obra':'Darío Cantón, Materiales para el estudio de la sociología política en la Argentina (1968), tomo II', 'fuente':str(source.relative_to(PROJECT)), 'sha256':sha, 'revision':'Todas las filas transcritas visualmente. No se imputan blancos, nulos ni cifras faltantes.', 'criterio_1931_1942':'Selección publicada por Cantón: excluyó los distritos donde no ganó la oposición por presunción de fraude. No certifica ausencia absoluta de irregularidades.'}
        (folder/f'canton_{year}.json').write_text(json.dumps({'metadatos':meta,'paginas':subset}, ensure_ascii=False,indent=2), encoding='utf-8')
        fields=['anio','tomo','pagina_pdf','pagina_libro','provincia','eleccion','categoria','unidad','circunscripcion','columna','concepto','valor','marca']
        cells=[]
        md=[f'# Cantón: {year}', '', 'Transcripción visual de las tablas del tomo II. Se conservan las cifras y las agrupaciones publicadas. `*`: sin dato. `**`: incluido en otra unidad o no considerado, según el original. Las marcas no equivalen a cero.', '']
        if year in (1937,1940):md+=['Selección de distritos de Cantón bajo el criterio explicado en la introducción del tomo I (p. XVI). No debe interpretarse como certificación de ausencia de toda irregularidad.', '']
        for p in subset:
            md += [f"## {p['provincia']} · PDF {p['pagina_pdf']} · libro {p['pagina_libro']}", '', p['eleccion']+'; '+p['categoria']+'.', '', '; '.join(f'{c}: {label}' for c,label in p['columnas'].items()), '', '| Unidad | '+' | '.join(map(str,p['columnas']))+' |', '|---|'+'---:|'*len(p['columnas'])]
            for r in p['filas']:
                label=r['unidad']+(f" ({r['circunscripcion']})" if r['circunscripcion'] is not None else '')
                md += ['| '+label+' | '+' | '.join(str(v) if v is not None else r['marcas'][c] for c,v in r['valores'].items())+' |']
                for c,label in p['columnas'].items():
                    cells.append({**{k:p[k] for k in fields if k in p},'unidad':r['unidad'],'circunscripcion':r['circunscripcion'],'columna':c,'concepto':label,'valor':r['valores'][c],'marca':r['marcas'].get(c,'')})
            md+=['']
        (folder/f'TRANSCRIPCION_{year}.md').write_text('\n'.join(md),encoding='utf-8')
        with (folder/f'canton_{year}.csv').open('w',encoding='utf-8-sig',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(cells)
        # En 1946 muchas tablas omiten blancos/nulos: una suma menor no prueba un error.
        sums=[]
        for p in subset:
            for r in p['filas']:
                vals=list(r['valores'].values())
                if all(v is not None for v in vals) and (sum(vals[2:])>vals[1] or year==1937 and p['provincia']!='Capital Federal' and sum(vals[2:])!=vals[1] or year==1940 and p['provincia']=='Tucumán' and sum(vals[2:])!=vals[1]):
                    sums.append({'pagina_pdf':p['pagina_pdf'],'unidad':r['unidad'],'votantes':vals[1],'suma_columnas':sum(vals[2:]),'diferencia':sum(vals[2:])-vals[1]})
        control={'paginas':len(subset),'distritos':len({p['provincia'] for p in subset}),'filas':sum(len(p['filas']) for p in subset),'celdas':len(cells),'numeros':sum(c['valor'] is not None for c in cells),'marcas':dict(Counter(c['marca'] for c in cells if c['marca'])),'alertas_aritmeticas':sums,'sha256_fuente':sha,'nota':'Las alertas se cotejan con el impreso; nunca se corrigen por residuo. La suma de partidos puede ser menor que votantes por categorías omitidas en la tabla.'}
        (folder/f'CONTROL_{year}.json').write_text(json.dumps(control,ensure_ascii=False,indent=2),encoding='utf-8')
        print(year, {k:v for k,v in control.items() if k not in ('alertas_aritmeticas','nota','sha256_fuente')})
        print('Alertas:',sums)


if __name__=='__main__':main()
