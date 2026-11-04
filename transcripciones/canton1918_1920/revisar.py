"""Correcciones y reservas de la segunda lectura visual (principal). Idempotente."""
from pathlib import Path
import json
from exportar import ROOT

CORRECCIONES=[
 dict(anio=1918,pagina_pdf=44,unidad='San Nicolás',columna='4',antes=605,despues=695,motivo='Relectura ampliada del dígito central: 695; el cotejo con Lupu señaló la discrepancia, sin sustituir la imagen.'),
 dict(anio=1918,pagina_pdf=44,unidad='Santa Lucía',columna='5',antes=4217,despues=4247,motivo='Relectura ampliada: 4.247.'),
 dict(anio=1918,pagina_pdf=44,unidad='Socorro',columna='6',antes=None,despues=1368,motivo='Cifra resuelta en recorte original ampliado: 1.368; antes marcada ilegible.'),
 dict(anio=1918,pagina_pdf=44,unidad='Vélez Sarsfield',columna='5',antes=None,despues=2286,motivo='Cifra resuelta en recorte original ampliado: 2.286; antes marcada ilegible.'),
]
FUENTES={
 44:'Para inscriptos y votantes: La Nación del 4 de mayo de 1918. Para partidos: La Nación, 7, 8, 10, 11, 12, 17, 18, 19 y 20 de abril de 1922. El año 1922 está impreso así, pese al encabezado 1918; no se corrige ni se presupone una errata.',
 45:'Inscriptos: La Nación, 3 de marzo de 1918; partidos: La Nación, 7 de abril de 1918. Fuente y clave al pie de PDF 48, común a las cuatro páginas de Buenos Aires.',
 49:'Partidos: La Prensa, 6 de marzo de 1918.',
 50:'Todos los datos: Anuario Estadístico, Provincia de Córdoba, año 1923. Es el año de la publicación citada, no una reasignación del año electoral.',
 51:'Partidos: La Nación, 10 de marzo de 1918.',
 52:'Partidos: La Prensa, 6 y 10 de marzo de 1918.',
 53:'Votantes: La Nación, 9, 10, 12 y 13 de marzo de 1918; partidos: esos periódicos más La Nación del 4 de abril de 1918.',
 54:'Votantes: La Nación, 8 y 4 de abril de 1918; partidos: La Nación, 8 de abril de 1922. La fecha 1922 está impresa así, pese al encabezado 1918; pendiente de cotejo primario.',
 56:'Inscriptos: La Nación, 8 de marzo de 1920. Votantes: La Prensa, 24 de marzo de 1924. Partidos: los periódicos mencionados más La Nación, 7 de marzo de 1920. Se conserva el año 1924 impreso para votantes, pese al encabezado 1920; pendiente de cotejo primario.',
 57:'Votantes: La Nación, 9 de marzo de 1920. Partidos: ese periódico más La Nación, 8 y 27 de marzo de 1920. Fuente y clave al pie de PDF 60, común a las cuatro páginas de Buenos Aires.',
 61:'Todos los datos: Anuario Estadístico, Provincia de Córdoba, año 1923. Es el año de la publicación citada, no una reasignación del año electoral.',
 62:'Partidos: La Nación, 12 de marzo de 1920.',
 63:'Partidos: La Nación, 14 y 16 de marzo de 1920.',
 64:'Memoria del Ministerio del Interior, año 1920–21.',
 65:'Partidos: La Nación, 22 de marzo de 1920.',
 66:'Partidos: La Nación, 25 de marzo de 1920. Claves 4 Demócrata y 5 Unión Popular confirmadas visualmente por el principal.',
 67:'Partidos: La Nación, 27 de marzo de 1920.',
 68:'Partidos: La Nación, 19 de marzo de 1920.',
}
for i in (46,47,48):FUENTES[i]=FUENTES[45]
for i in (58,59,60):FUENTES[i]=FUENTES[57]

def main():
    for year in (1918,1920):
        folder=ROOT/f'transcripciones/canton{year}';path=folder/f'canton_{year}.json'
        doc=json.loads(path.read_text(encoding='utf-8'))
        text=(folder/f'manual{year}.txt').read_text(encoding='utf-8')
        for c in [r for r in CORRECCIONES if r['anio']==year]:
            pg=next(p for p in doc['paginas'] if p['pagina_pdf']==c['pagina_pdf'])
            row=next(r for r in pg['filas'] if r['unidad']==c['unidad'])
            assert row['valores'][c['columna']] in (c['antes'],c['despues']),c
            row['valores'][c['columna']]=c['despues'];row['marcas'].pop(c['columna'],None)
            row['nota_revision']=c['motivo']
            lines=text.splitlines()
            for i,line in enumerate(lines):
                if line.startswith(c['unidad']+'/'):
                    prefix,vals=line.split('|');vals=vals.split();vals[int(c['columna'])-1]=str(c['despues']);lines[i]=prefix+'|'+' '.join(vals)
            text='\n'.join(lines)+'\n'
        for pg in doc['paginas']:
            pg['fuentes_impresas']=FUENTES[pg['pagina_pdf']]
            if pg['pagina_pdf'] in (44,54,56):
                pg['reserva_cronologica']='La fuente periodística impresa cita un año posterior al encabezado. Transcripción del libro, atribución cronológica pendiente de corroboración primaria; no usar para completar otro año.'
            if pg['pagina_pdf']==45:
                r=next(r for r in pg['filas'] if r['unidad']=='Balcarce')
                r['nota_revision']='Conservador: se conserva lectura 174; dígito central débil, alternativa 144 en Lupu. No se considera resuelta con certeza la discrepancia: pendiente de cotejo primario.'
        doc['metadatos']['revision']='Primera lectura visual por subagente Terra; revisión focalizada independiente del principal en dudas, claves y alertas; cotejo diagnóstico con Lupu–Stokes, sin reemplazar cifras por esa base. Inscriptos y votantes releídos por el transcriptor. No equivale a segunda lectura exhaustiva de todas las celdas.'
        doc['metadatos']['revision_focalizada']='Ver ../canton1918_1920/REVISION.md y CORRECCIONES.json.'
        path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/f'manual{year}.txt').write_text(text,encoding='utf-8')
    (Path(__file__).parent/'CORRECCIONES.json').write_text(json.dumps(CORRECCIONES,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Revisión aplicada: dos digitaciones corregidas, dos ilegibles resueltos; sin imputación.')

if __name__=='__main__':main()
