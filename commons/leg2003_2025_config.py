"""Registro de paquetes legislativos derivados de 2009, con reservas explícitas."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
DATES={2003:'27 de abril al 23 de noviembre de 2003',2005:'23 de octubre de 2005',2007:'28 de octubre de 2007',2011:'23 de octubre de 2011',2015:'25 de octubre de 2015',2017:'22 de octubre de 2017',2019:'27 de octubre de 2019',2021:'14 de noviembre de 2021',2023:'22 de octubre de 2023',2025:'26 de octubre de 2025'}

def register(ATLAS,GEOM,GEOM_SHORT,HOLD_TEXT):
    meta_path=ROOT/'datos/fuentes_leg2003_2025/logos_metadata.json'
    metadata=json.loads(meta_path.read_text(encoding='utf8')) if meta_path.exists() else {}
    metadata={p['title'][5:]:p for p in metadata.values() if p.get('imageinfo')}
    comp_path=ROOT/'datos/fuentes_leg2003_2025/complementos_departamentales.json'
    complements=json.loads(comp_path.read_text(encoding='utf8')) if comp_path.exists() else []
    for y,date in DATES.items():
        p=ROOT/f'mapas/mapa{y}/control_cobertura.json'
        if not p.exists():continue
        report=json.loads(p.read_text(encoding='utf8'))
        g=f'leg{y}';GEOM[g]=report['geometry'];GEOM_SHORT[g]=report['geometry'].lower()
        missing=report['missing']+(['Antártida Argentina'] if report['antartida_sin_dato'] else [])
        hold=[]
        if missing:
            key=f'faltantes_leg{y}';hold=[key];HOLD_TEXT[key]='Faltan resultados desagregados: '+', '.join(missing)+'. Resolver antes de publicar el atlas completo.'
        logos=report['logos'];drop=[x['code'] for x in logos if x['archivo'] and (x['reserva_epoca'] or 'SA' in x['licencia'] or 'proyecto' in x['licencia'])]
        doubtful=[x for x in logos if x['archivo'] and not x['fuente'].startswith('https://commons.wikimedia.org/')]
        hlogo=[]
        if doubtful:
            key=f'licencias_leg{y}';hlogo=[key];HOLD_TEXT[key]='Revisar licencias/fechas de los logos reutilizados antes de subir las versiones con emblemas. La variante con siglas omite estos emblemas.'
        src=(f'dat.ar (datar.info), CSV departamental original conservado en raw/; cotejado por sumas de listas y métricas. No se imputa ninguna cifra ausente.' if y==2003 else
             f'PolAr_Data (electorArg), resultados provisorios INDRA / Atlas Electoral de Andy Tow por mesa, agregados por departamento y circunscripción.' if y<2011 else
             f'Dirección Nacional Electoral, Resultados Provisionales Elecciones {y}, datos por mesa publicados en datos.gob.ar y agregados por departamento/comuna.')
        comp=[c for c in complements if c['year']==y]
        cne=[c for c in comp if c['pdf'].startswith('padron_publica/')];dine=[c for c in comp if c not in cne]
        if dine:src+=' '+'; '.join(sorted({c['name'] for c in dine}))+': escrutinio definitivo de la Dirección Nacional Electoral (PDF por distrito de elecciones.gob.ar, copia de la Wayback Machine), porque la fuente principal no trae esas unidades.'
        if cne:src+=' '+'; '.join(sorted({c['name'] for c in cne}))+': escrutinio definitivo de la Cámara Nacional Electoral («Consulta de Escrutinio por Zona», padron.gob.ar/publica), porque la fuente principal no trae esa unidad.'
        ATLAS[str(y)]=dict(folder=f'mapa{y}',html=f'atlas_{y}.html',dataset=f'dataset_{y}.json',article=f'Elecciones legislativas de Argentina de {y}',
             tipo='elecciones legislativas (diputados nacionales)',fecha=date,varones=False,geom=g,antartida=True,
             cats_extra=['Election maps of Argentine Chamber of Deputies elections'],votos=[src],
             logos=sorted({x['commons_title'].replace('_',' ') for x in logos if x['archivo'] and x['commons_title']}),
             hold=hold,hold_logos=hlogo,sin_logo=drop,
             avisos=[f'El resultado nacional sale de la tabla del artículo de Wikipedia; el mapa utiliza los resultados territoriales de la fuente indicada. Los positivos de la base suman {report["base_positivos"]:,} y Wikipedia {report["wikipedia_positivos"]:,}. No se ajustaron las cifras para forzar igualdad.',
                     'Alianzas y colores de las tablas de Wikipedia (instantáneas y revisiones en fuentes_leg2003_2025/); mapeo de todas las listas y diferencias por bloque en el LEEME y CSV del atlas.',
                     'Sólo los bloques con alguna unidad ganada aparecen en la leyenda nacional. Las demás listas permanecen en las fichas de cada unidad.',
                     'Geometría histórica: '+report['geometry']+'. El límite La Paz/Choya se conserva como en el shapefile histórico.',
                     'Faltantes sin imputación: '+(', '.join(missing) if missing else 'ninguno')+'.',
                     'Logos tomados del artículo de la elección o del partido. Las reconstrucciones posteriores se anotan como diseño de época no verificado. Ver logos_usados.json y LICENCIAS.md.']+report['corrections'])
        if y==2003:ATLAS[str(y)]['fecha_en']='27 April to 23 November 2003'
        ATLAS[str(y)]['fecha_verificada']=True
        ATLAS[str(y)]['capital_division']='por circunscripción' if y<=2007 else 'por comuna'
        ATLAS[str(y)]['geometry_en']=('2001 department boundaries and 28 electoral constituencies in Buenos Aires city' if y<=2007 else '2010 department boundaries, Buenos Aires city communes and the later Lezama subdivision'+(' and Tolhuin subdivision' if y>=2019 else ''))
        if report.get('solid'):
            ATLAS[str(y)]['solido']=(', '.join(report['solid']),'color provincial del definitivo DINE; la fuente declara que no recibió resultados por departamento, por lo que no se reparten votos')
        if any('SA' in x['licencia'] for x in logos if x['archivo']):ATLAS[str(y)]['map_license']='cc-by-sa-4.0'
        ATLAS[str(y)]['description_es']=(
            f'El cartel nacional usa la tabla de Wikipedia y el mapa los votos territoriales de la fuente citada; no se ajustan los votos locales para forzar igualdad. '
            f'Positivos disponibles en la base: {report["base_positivos"]:,}; tabla nacional: {report["wikipedia_positivos"]:,}. '
            +('Resultados desagregados pendientes (beige): '+', '.join(missing)+'. ' if missing else 'Cobertura territorial sin departamentos pendientes. ')
            +('La Pampa se muestra como resultado provincial sólido, sin atribuir votos a sus departamentos. ' if y==2003 else '')
            +'Las reconstrucciones de emblemas posteriores a la elección tienen diseño de época no verificado y una variante con siglas.')
        ATLAS[str(y)]['description_en']='National totals follow the Spanish Wikipedia table; territorial votes follow the cited electoral sources. Missing or non-disaggregated results are beige; no votes were imputed. Later logo reconstructions have an acronym-only alternative.'
        ATLAS[str(y)]['logos_omitidos_siglas']=[x['commons_title'].replace('_',' ') for x in logos if x['code'] in drop and x['commons_title']]
        attrs=[]
        for x in logos:
            if not x['archivo'] or not x['commons_title']:continue
            title=x['commons_title'].replace('_',' ');p=metadata.get(title)
            if not p:continue
            ext=p['imageinfo'][0].get('extmetadata',{})
            attrs.append(dict(title=title,author=ext.get('Artist',{}).get('value','Autor identificado en la página original de Commons'),license=ext.get('LicenseShortName',{}).get('value','ver página original')))
        ATLAS[str(y)]['logos_atribucion']=attrs

PASO_DATES={2011:'14 de agosto de 2011',2013:'11 de agosto de 2013',2015:'9 de agosto de 2015',2017:'13 de agosto de 2017',2019:'11 de agosto de 2019',2021:'12 de septiembre de 2021',2023:'13 de agosto de 2023'}
# mapa presidencial de Commons del que se recortó cada bloque (logos/bloques_presidenciales/extraer_bloques.py)
BLK_YEAR={n:y for y,ns in {2003:['menem','fpv03','recrear','mnp','ari'],2007:['fpv07','cc','una07','frejuli07','pu07'],2011:['fpv11','fap','udeso','cf11','fp11'],
          2015:['fpv15','cambiemos','una15','cf15'],2019:['fdt','sisepuede','consenso'],2023:['up','lla','jxc23','hacemos']}.items() for n in ns}
PASO_KEYS=['2011paso','2011pasodip','2013paso','2015paso','2015pasodip','2017paso','2019paso','2019pasodip','2021paso','2023paso','2023pasodip']

def register_paso(ATLAS,GEOM,GEOM_SHORT,HOLD_TEXT):
    """Paquetes de las PASO 2011-2023: geometría y textos del atlas general del año; logos de la general o de los mapas presidenciales."""
    def load(k,name):
        p=ROOT/f'mapas/mapa{k}/{name}'
        return json.loads(p.read_text(encoding='utf8')) if p.exists() else None
    gen_logos={}   # img del legend -> entrada de logo de una general 2011-2025
    for y in DATES:
        ds,rep=load(y,f'dataset_{y}.json'),load(y,'control_cobertura.json')
        if not ds or not rep:continue
        for x in rep['logos']:
            img=ds['candidates'].get(x['code'],{}).get('img')
            if img and x.get('archivo'):gen_logos.setdefault(img,[]).append(dict(x,year=y))
    for k in PASO_KEYS:
        rep,ds=load(k,'control_cobertura.json'),load(k,f'dataset_{k}.json')
        if not rep:continue
        y=rep['year'];pres=rep['cargo']=='presidente';base=ATLAS[str(y)]
        g=f'paso{k}';GEOM[g]=rep['geometry'];GEOM_SHORT[g]=rep['geometry'].lower()
        logos,drop,doubt=set(),[],[]
        for x in rep['logos']:
            if x.get('bloque'):logos.add(f"Elecciones presidenciales de Argentina de {BLK_YEAR[x['bloque']]} - Resultados.png");continue
            hits=gen_logos.get(ds['candidates'][x['code']].get('img'),[])   # la general del mismo año o la más cercana
            e=min(hits,key=lambda h:abs(h['year']-y)) if hits else None
            if not e:
                if y==2013:continue   # 2013 conserva la lista de logos verificada de su atlas general
                doubt.append(x['code']);continue
            if e.get('commons_title'):logos.add(e['commons_title'].replace('_',' '))
            if e.get('bloque_wikipedia'):logos.add(f"Elecciones presidenciales de Argentina de {BLK_YEAR[Path(e['bloque_wikipedia']).stem]} - Resultados.png")
            if e['reserva_epoca'] or 'SA' in e['licencia'] or 'proyecto' in e['licencia']:drop.append(x['code'])
            elif not e['fuente'].startswith('https://commons.wikimedia.org/'):doubt.append(x['code'])
        if y==2013:logos|=set(base['logos'])
        missing=rep['missing']+(['Antártida Argentina'] if rep['antartida_sin_dato'] else [])
        hold,hlogo=[],[]
        if missing:
            key=f'faltantes_{k}';hold=[key];HOLD_TEXT[key]='Faltan resultados desagregados: '+', '.join(missing)+'. Resolver antes de publicar el atlas completo.'
        if doubt:
            key=f'licencias_{k}';hlogo=[key];HOLD_TEXT[key]='Revisar licencias/fechas de los logos reutilizados antes de subir las versiones con emblemas. La variante con siglas omite estos emblemas.'
            drop+=[c for c in doubt if c not in drop]
        cargo='presidente' if pres else 'diputados nacionales'
        art=rep['national']['art']
        internas=rep.get('internas') or []
        ATLAS[k]=dict(folder=f'mapa{k}',html=f'atlas_{k}.html',dataset=f'dataset_{k}.json',article=art,year=str(y),
            filename_prefix=f'{art} ({cargo})',
            tipo=f'elecciones primarias abiertas, simultáneas y obligatorias (PASO) de {cargo}',fecha=PASO_DATES[y],varones=False,geom=g,antartida=True,
            cats_extra=[f'{y} Argentine primary elections','Election maps of Argentina']+([] if pres else ['Election maps of Argentine Chamber of Deputies elections']),
            votos=[f'Dirección Nacional Electoral, resultados provisionales de las PASO {y}, datos por mesa (argentina.gob.ar), agregados por departamento/comuna. Cada agrupación suma sus listas internas.'],
            logos=sorted(logos),hold=hold,hold_logos=hlogo,sin_logo=drop,
            avisos=[f"El resultado nacional sale de la {rep['metrics_src']}.",
                    'Gana la agrupación (suma de sus listas internas); la ficha de cada unidad muestra cada lista.'
                    +(f" Modos de interna ({', '.join(internas)}): precandidato más votado dentro de la agrupación en cada unidad." if internas else ''),
                    ('Agrupaciones, colores y logos de los mapas presidenciales de la Wikipedia (bloques de leyenda, CC0).' if pres else
                     'Bloque, color y logo de la misma agrupación en la elección general del año; las que no siguieron a la general y ganan alguna unidad llevan bloque propio.'),
                    'Sólo los bloques con alguna unidad ganada aparecen en la leyenda nacional.',
                    'Geometría histórica: '+rep['geometry']+'. El límite La Paz/Choya se conserva como en el shapefile histórico.',
                    'Faltantes sin imputación: '+(', '.join(missing) if missing else 'ninguno')+'.']+rep.get('corrections',[]))
        for f in ('fecha_verificada','capital_division','geometry_en','logos_atribucion'):
            if f in base:ATLAS[k][f]=base[f]
        ATLAS[k]['description_es']=(f'Primarias (PASO) de {cargo}: gana la agrupación, sumando sus listas internas. Votos del escrutinio provisorio por mesa de la DINE. '
            +('Resultados desagregados pendientes (beige): '+', '.join(missing)+'. ' if missing else 'Cobertura territorial sin departamentos pendientes. '))
        ATLAS[k]['description_en']=f'Argentine open primaries (PASO), {"presidential" if pres else "national deputies"}: each alliance adds up its internal lists. Provisional count by polling station (DINE). Missing results are beige; no votes were imputed.'
