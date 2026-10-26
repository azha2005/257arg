"""Registro de paquetes legislativos derivados de 2009, con reservas explícitas."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
DATES={2003:'27 de abril al 23 de noviembre de 2003',2005:'23 de octubre de 2005',2007:'28 de octubre de 2007',2011:'23 de octubre de 2011',2015:'25 de octubre de 2015',2017:'22 de octubre de 2017',2019:'27 de octubre de 2019',2021:'14 de noviembre de 2021',2023:'22 de octubre de 2023',2025:'26 de octubre de 2025'}

def register(ATLAS,GEOM,GEOM_SHORT,HOLD_TEXT):
    meta_path=ROOT/'datos/fuentes_leg2003_2025/logos_metadata.json'
    metadata=json.loads(meta_path.read_text(encoding='utf8')) if meta_path.exists() else {}
    metadata={p['title'][5:]:p for p in metadata.values() if p.get('imageinfo')}
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
