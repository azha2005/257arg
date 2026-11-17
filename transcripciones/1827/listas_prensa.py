"""Listas de candidatos de la Gaceta Mercantil 1103-1110 (julio de 1827), transcriptas a ojo de los PDF de la Hemeroteca
Digital de la BNMM (sin OCR). Escribe listas_prensa_1827.csv: un renglón por candidato, con el electo que le corresponde en
electos_1827.csv (si salió electo) y la nota de la identificación cuando hay reserva.

La lista «Unos enemigos del Imperio Brasilero» (N1103) está aparte, en lista_N1103_enemigos_del_imperio.csv, con su
asignación por sección (ciudad y campaña); el atlas usa para ella la columna en_lista_N1103 de electos_1827.csv.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (edición, fecha, firma, ámbito, ubicación en el número, candidatos en el orden impreso)
LISTAS = [
    ('N1103', '1827-07-11', 'Un Porteño', 'ciudad', 'p. 2, cols. 3-4',
     'Juan José Anchorena|Félix Álzaga|José María Escalada|Miguel Riglos|Pedro Lezica|Manuel Vicente Maza|Manuel Hermenegildo Aguirre|'
     'Pedro Capdevila|Manuel Moreno|José María Somalo|Miguel Marín|José Julián Arriola|Pedro Medrano|Pedro Trapani|Juan Pino|'
     'Juan José Viamont|Justo García Valdez|Blas José Pico|Nicolás Anchorena|Braulio Costa|Eugenio Villanueva|Marcos Balcarce|'
     'Juan Ramón Balcarce|Miguel Soler'),
    ('N1104', '1827-07-12', 'Unos Provincianos', 'ciudad', 'p. 2, col. 3, y p. 3, col. 1',
     'Bernardino Rivadavia|Manuel García|Valentín Gómez|Julián S. de Agüero|José M. Roxas|Manuel Arroyo|Bernardo Ocampo|'
     'Valentín San Martín|Alejo Castex|Manuel A. Castro|Juan Cosio|Miguel Villegas|Roque Peña|Bartolo Cueto|Manuel Garmendia|'
     'Pedro J. Echegaray|Juan Alagón|José Cayetano Pico|Damián Castro|Blas Pico|Braulio Costa|Julián Panelo|Estanislao Zabaleta|'
     'Mariano Zabaleta'),
    ('N1104', '1827-07-12', 'Los patriotas libres y de ideas republicanas', 'ciudad', 'p. 3, col. 1',
     'Pedro Medrano|El Cura de Monserrat, Ruiz|Manuel Dorrego|Juan Manuel Rojas|Pedro Cavia|Ugarteche|Marcos Balcarce|'
     'Rafael Saavedra|Vicente A. Echevarría|Juan José Anchorena|Juan José Viamont|Miguel Soler|Tomás Anchorena|José María Escalada|'
     'El Sr. Moreno|Pedro Agrelo|Juan Pedro Aguirre|Cornelio Saavedra|Bartolomé Muñoz|Victorio García Zúñiga|Grela|'
     'Nicolás Anchorena|Felipe Arana|Enrique Martínez, general|Manuel Obligado'),
    ('N1104', '1827-07-12', 'Unos Ciudadanos', 'ciudad', 'p. 3, cols. 1-2',
     'José Miguel Díaz Vélez|Juan Pino|Tomás Guido|Luis Dorrego|Félix Álzaga|José María Escalada|José Joaquín Ruiz|'
     'Gregorio Perdriel|Justo García Valdez|Ángel Molino Torres|Manuel Insiarte|José María Coronell|Abelino Díaz|'
     'José Antonio Villanueva|Pedro Lezica|Gregorio Gómez|Braulio Costa|Miguel Estanislao Soler|Ignacio Núñez|Julián Panelo|'
     'Manuel H. de Aguirre|Bernabé Escalada|Manuel Maza|Faustino Lezica'),
    ('N1105', '1827-07-13', 'Unos Imparciales', 'ciudad', 'p. 2, col. 2',
     'Somellera|Pazos|Juan P. Aguirre|Mariano Fragueyro|Bernabé Escalada|Faustino Lezica|Manuel Hermenegildo Aguirre|'
     'Manuel B. Gallardo|Abelino Díaz|Manuel Insiarte|Justo García Valdés|Tomás Guido|José Miguel Díaz Vélez|Ruiz|'
     'José Ignacio Garmendia|Estanislao Zavaleta|Braulio Costa|Pedro José Echegaray|Roque Peña|Juan Cossio|Manuel Antonio Castro|'
     'Valentín S. Martín|José María Rojas|Valentín Gómez'),
    ('N1105', '1827-07-13', 'Un Porteño', 'ciudad', 'p. 2, col. 4',
     'Ramón E. Anchoris|Félix Álzaga|Ignacio Grela|Domingo Achega|Enrique Martínez, general|Juan J. Viamont, general|'
     'José J. Arriola|José María Escalada|Manuel Vicente Maza|Juan J. Anchorena|Ángel Molino Torres|Avelino Díaz|'
     'Francisco Tollo, coronel|Pedro Medrano|Julián Panelo|Braulio Costa|Pedro Capdevila|Pedro J. Agrelo|Manuel Insiarte|'
     'Miguel Azcuénaga, general|Tomás Guido, general|Juan Madera|Vicente A. Echevarría'),
    ('N1105', '1827-07-13', 'Amantes del orden', 'ciudad', 'p. 2, col. 3',
     'Juan José Anchorena|Manuel Obligado|Pedro Medrano|Juan Manuel Rojas|Juan José Viamont|Juan Ramón Balcarce|'
     'Nicolás Anchorena|Pedro Lezica|Joaquín Ruiz|Juan Pino|Félix Álzaga|Victorio García Zúñiga|Pedro Cavia|Manuel Dorrego|'
     'Ugarteche|Aguiar|Rafael Saavedra|Rafael Pereyra Lucena|José María Escalada|Manuel Moreno|Gregorio Perdriel|'
     'Manuel Luzurriaga|Luis Dorrego|Justo García Valdez'),
    ('N1108', '1827-07-17', 'Nómina sin firma para elegir', 'ciudad', 'p. 2, cols. 2-3',
     'Nicolás Anchorena|Manuel Inciarte|Juan J. Viamont|José María Escalada|Juan P. Aguirre|Mariano Fragueiro|Faustino Lezica|'
     'Abelino Díaz|Francisco Wright|Somellera|Justo G. Valdez|José Rondeau|J. Pasos|Tomás Guido|Joaquín Ruiz|'
     'Juan José Zernadas|Roque Peña|Manuel A. Castro|Braulio Costa|Julián Panelo|Juan B. Morón|Manuel H. Aguirre|'
     'Bernardo Escalada|Cornelio Saavedra|Juan Pino|Juan J. Anchorena|Juan P. Aguirre|José M. Somalo|Gregorio Perdriel|'
     'José L. Domínguez|Miguel Riglos|Blas J. Pico|Pedro Lezica|Manuel Obligado|Pedro Medrano|Manuel Dorrego|'
     'Juan Ramón Balcarce|Victorio G. Zúñiga|Manuel V. Maza|Francisco Tollo|Pedro Capdevila|P. J. Agrelo|José O. Feliu|'
     'Juan M. Rosas|Luis Dorrego|Pedro J. Campos|Pedro J. Echegaray|Juan Cano'),
    ('N1108', '1827-07-17', 'Un Patriota antes del año 10', 'ciudad', 'p. 2, cols. 3-4',
     'Juan Miguens|Luis Dorrego|Félix Álzaga|Juan M. Rosas|Pascual Costa|Nicolás Anchorena|Félix Castro|Manuel Moreno|'
     'Pedro Cavia|Ladislao Martínez|Felipe Piñeyro|José María Escalada|Julián Arriola|Santiago Tobal|Miguel Marmol|'
     'Francisco Wright|Pedro Trapani|Juan Pedro Aguirre|Mariano Ibarrola|Ramón Balcarce|Juan Alsina|Manuel Cueto|'
     'Patricio Linch|Juan Domingo Banega'),
    ('N1109', '1827-07-18', 'Unos Porteños Federales', 'ciudad', 'p. 2, col. 1',
     'Julián Gregorio Espinoza|Tomás Antonio Valle|Juan Manuel Rosas|Pedro Medrano|Pedro José Agrelo|Pedro Trapani|'
     'Manuel Obligado|Manuel Escalada|Vicente Maza|José Vidal|Matías Irigoyen|José María Escobar|Mariano B. Rolón|'
     'Hilario Sosa|Cosme Argerich|Sebastián Lezica|José Antonio Villanueva|Tomás Aguiar|Cornelio Saavedra|Juan José Bosch|'
     'Victorio García de Zúñiga|Juan José Viamont|Francisco Tollo|Domingo Trillo'),
    ('N1109', '1827-07-18', 'Un Porteño Imparcial', 'sin especificar', 'p. 1, col. 4',
     'Vicente Anastasio Echeverría|Ferreira|Ugarteche|Mariano Maza|Celestino Vidal|José María Yeves|Rafael Pereira Lucena|'
     'Luis Dorrego|Francisco Reyes y Conti|José Antonio Chilavert|Ruperto Albarellos|Braulio Costa|Mariano Rolón|'
     'Marcelino Carranza|Juan Martín Pueyrredón|Rafael Saavedra|Dongo|Ángel Saravia|Pedro Cavia|Pedro Medrano|Mariano Tagle|'
     'N. Albizuri, teniente coronel|Carrasco|José Viamont|Aguiar|Tomás Lorea|Valle|Bautista|Tomás Boyzo|Juan de la Cruz Varela'),
    ('N1110', '1827-07-19', 'Unos Porteños', 'ciudad', 'p. 2, cols. 1-2',
     'Victoriano García de Zúñiga|Pedro Medrano|Juan José Anchorena|Félix Álzaga|Mateo Vidal|Felipe Senillosa|Juan del Pino|'
     'Manuel Obligado|Rafael Pereira Lucena|Luis Dorrego|Pedro Lezica|Pedro Trapani|José Julián Arriola|José María Somalo|'
     'Juan José Viamont|Julián de Gregorio Espinosa|Juan José Cernadas|Ladislao Martínez|Agustín Francisco Wright|'
     'Vicente Anastasio de Echevarría|Pedro F. Cavia|Felipe Arana|Manuel Dorrego|Juan Ramón Balcarce|Manuel V. Maza'),
    ('N1110', '1827-07-19', 'Unos Imparciales', 'ciudad', 'p. 2, cols. 2-3',
     'Pedro Medrano|José I. Ruiz|Vicente A. Echavarría|Manuel Obligado|Juan Manuel Rosas|Juan Ramón Balcarce|'
     'Juan José Anchorena|Marcelo Gamboa|Miguel Gutiérrez|Domingo Achega|Félix Álzaga|Felipe Arana|Domingo Zapiola|'
     'Francisco Planes|Nicolás Anchorena|Pedro Pablo Vidal|Manuel Escalada|Félix Eloriondo Palacio|Vicente Maza|'
     'Juan J. Viamont|José León Banegas|Manuel H. Aguirre|Celestino Vidal|José María Escalada'),
]

# nombre impreso -> electo de electos_1827.csv, o (electo, nota) si la identificación tiene reserva
ALIAS = {
    'Félix Álzaga': 'Félix Álzaga', 'Juan Ramón Balcarce': 'Juan Ramón Balcarce',
    'Ramón Balcarce': ('Juan Ramón Balcarce', 'impreso «D. Ramón Balcarce»'),
    'Victorio García Zúñiga': 'Victorio García de Zúñiga', 'Victorio García de Zúñiga': 'Victorio García de Zúñiga',
    'Victorio G. Zúñiga': 'Victorio García de Zúñiga', 'Victoriano García de Zúñiga': ('Victorio García de Zúñiga', 'impreso «Victoriano»'),
    'Ignacio Grela': 'Ignacio Grela', 'Grela': 'Ignacio Grela', 'Cosme Argerich': 'Cosme Argerich', 'Felipe Arana': 'Felipe Arana',
    'Manuel Hermenegildo Aguirre': 'Manuel Aguirre de Lajarrota', 'Manuel H. de Aguirre': 'Manuel Aguirre de Lajarrota',
    'Manuel H. Aguirre': 'Manuel Aguirre de Lajarrota',
    'Pedro Medrano': 'Pedro Medrano', 'Marcelo Gamboa': 'Marcelo Gamboa',
    'José Joaquín Ruiz': 'José Joaquín Ruiz', 'El Cura de Monserrat, Ruiz': 'José Joaquín Ruiz', 'Joaquín Ruiz': 'José Joaquín Ruiz',
    'Ruiz': ('José Joaquín Ruiz', 'impreso «Dr. Ruiz»'), 'José I. Ruiz': ('José Joaquín Ruiz', 'impreso «José I. Ruiz»'),
    'Rafael Pereyra Lucena': 'Pereyra Lucena', 'Rafael Pereira Lucena': 'Pereyra Lucena',
    'Manuel Vicente Maza': 'Manuel Vicente Maza', 'Manuel V. Maza': 'Manuel Vicente Maza', 'Manuel Maza': 'Manuel Vicente Maza',
    'Vicente Maza': ('Manuel Vicente Maza', 'impreso «Vicente Maza»'),
    'José María Escalada': 'José María Escalada', 'Felipe Senillosa': 'Felipe Senillosa',
    'Aguiar': 'Tomás Aguiar', 'Tomás Aguiar': 'Tomás Aguiar',
    'Manuel Obligado': 'Manuel Obligado', 'Gregorio Perdriel': 'Gregorio Perdriel', 'Juan Pino': 'Juan del Pino', 'Juan del Pino': 'Juan del Pino',
    'Ladislao Martínez': 'Ladislao Martínez', 'Braulio Costa': 'Braulio Costa', 'Bernabé Escalada': 'Bernabé Escalada',
    'Vicente A. Echevarría': 'Vicente Anastasio Echevarría', 'Vicente Anastasio Echeverría': 'Vicente Anastasio Echevarría',
    'Vicente Anastasio de Echevarría': 'Vicente Anastasio Echevarría', 'Vicente A. Echavarría': 'Vicente Anastasio Echevarría',
    'Tomás Antonio Valle': 'Tomás Antonio Valle', 'Valle': ('Tomás Antonio Valle', 'impreso «Dr. Valle»'),
    'Celestino Vidal': 'Celestino Vidal', 'Juan José Viamont': 'Juan José Viamont', 'Juan J. Viamont': 'Juan José Viamont',
    'Juan J. Viamont, general': 'Juan José Viamont', 'José Viamont': ('Juan José Viamont', 'impreso «Dr. D. José Viamont»'),
    'Agustín Francisco Wright': 'Agustín Francisco Wright', 'Francisco Wright': ('Agustín Francisco Wright', 'impreso «Francisco Wright»'),
    'Domingo Achega': 'Domingo Achega', 'Valentín San Martín': 'Valentín San Martín', 'Valentín S. Martín': 'Valentín San Martín',
    'Luis Dorrego': 'Luis Dorrego', 'Nicolás Anchorena': 'Nicolás Anchorena',
    'José María Rojas': 'José María Rojas', 'José M. Roxas': 'José María Rojas',
}
NOTAS = {'Bernardo Escalada': 'podría ser Bernabé Escalada; no se cuenta como electo'}


def main():
    electos = {r['nombre']: r['seccion'] for r in csv.DictReader(open(HERE / 'electos_1827.csv', encoding='utf-8'))}
    rows = []
    for ed, fecha, firma, amb, ubic, txt in LISTAS:
        for i, c in enumerate(txt.split('|'), 1):
            a = ALIAS.get(c)
            e, nota = (a if isinstance(a, tuple) else (a, '')) if a else ('', NOTAS.get(c, ''))
            assert not e or e in electos, e
            rows.append(dict(edicion=ed, fecha=fecha, firma=firma, ambito=amb, ubicacion=ubic, orden=i, candidato=c,
                             electo=e, seccion_electo=electos.get(e, ''), nota=nota))
    with open(HERE / 'listas_prensa_1827.csv', 'w', encoding='utf-8', newline='') as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for ed, fecha, firma, *_ in LISTAS:
        rr = [r for r in rows if (r['edicion'], r['firma']) == (ed, firma)]
        print(ed, firma, len(rr), 'electos', sum(bool(r['electo']) for r in rr),
              'ciudad', sum(r['seccion_electo'] == 'Ciudad' for r in rr))
    # candidatos sin emparejar con el apellido de un electo, para revisar a mano
    apellidos = {n.split()[-1]: n for n in electos}
    for r in rows:
        if not r['electo']:
            for ap, n in apellidos.items():
                if ap in r['candidato']:
                    print('  revisar:', r['edicion'], r['firma'], '|', r['candidato'], '~', n)


if __name__ == '__main__':
    main()
