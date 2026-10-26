# Diputados nacionales 1912 — atlas por departamento (15-oct-2026)

`python build_1912.py` regenera `atlas_1912_diputados.html` (HTML autónomo, 1,7 MB) y `dataset_1912.json`. Es el build de 1914 con otra capa de datos. Vistas: GANÓ (bloque más votado), UCR, CON (conservadores) y PART (participación **provincial**).
Paquete para Commons en `../commons/1912/` (8 SVG + 4 PNG, sin subir). PNG: `../png_transparentes/mapa1912/` y `../png_blanco/mapa1912/`.

**Geometría:** departamentos del censo de 1914 (`Departamentos_1914`), el mapa más cercano a 1912 (el anterior es 1895, con bastantes menos partidos y departamentos) y el que usan Cantón y los expedientes para Capital (20 circunscripciones) y Córdoba. Los territorios nacionales no votaban (gris).

## Cobertura

| Qué | Unidades | Fuente |
|---|---|---|
| Capital Federal | 20 circunscripciones (Puerto no es unidad electoral) | Cantón (1968), t. II |
| Córdoba | 21 de 26 filas (5 sin cifra impresa: General Roca, Presidente Roque Sáenz Peña, Juárez Celman, Marcos Juárez, Punilla; gris «subsumidas») | Cantón |
| Mendoza | 16 unidades (Ciudad = polígono Capital; Luján = Luján de Cuyo) | 188 mesas del expediente 42-D-1912 |
| Santa Fe | 5 de 19: Rosario, Las Colonias, San Lorenzo, Vera, Belgrano; 14 en beige | diario *Santa Fe* 18, 20 y 23/4/1912 |
| Buenos Aires, Catamarca, Corrientes, Entre Ríos, Jujuy, La Rioja, Salta, San Juan, San Luis, Santiago del Estero, Tucumán | provincia entera en un color (`DATA.solid`) | tabla provincial de la Wikipedia |

Recuadros: Gran Mendoza, Área Metropolitana y Capital. Sin Tucumán, Gran San Juan ni Resistencia + Corrientes (esas provincias son de un solo color).

## Decisiones que conviene revisar

1. **Bloques como la tabla nacional de la Wikipedia.** «Partidos Conservadores» (#30D5C8) suma las diez filas conservadoras (283.745). Unión Nacional va como bloque propio, en el royalblue del artículo (#4169e1); queda cerca del azul oscuro de la Liga del Sur (#005C9E), que gana solo dos departamentos de Santa Fe, pero se distinguen. Unión Comunal, Defensa Rural y «Otros» van a «otros» (nunca ganan).
2. **Cada partido = votos de su primer candidato** (lista incompleta: se votaba por hasta dos tercios de los cargos; la Wikipedia da «votos al partido»). En Santa Fe se descartan los acompañantes de lista (Ávalos, Coronado, Valdez; Casablanca, Lagos, Lejarza; Regules, Saavedra Lamas, García Vieyra).
3a. **San Juan, quién era el oficialismo** (búsqueda del 15-oct-2026): el expediente 27-D-1912 no nombra a los partidos («los partidos políticos en lucha»). En el debate de diplomas, Juan B. Justo (Diario de Sesiones 1912, recogido en *La obra parlamentaria*, 1913, pp. 9 a 12) habla de «el partido que acaba de triunfar en San Juan» y de «el partido popular de San Juan», con «sus dos flamantes diputados» (Etchegaray y Albarracín, la lista que la Wikipedia llama Partido Oficial). Ese Partido Popular gobernó la provincia de 1907 a 1914; la Concentración Cívica (Garro, Brandam) reunió a los conservadores y a «algunos militantes del partido gobernante» tras la ley Sáenz Peña, y ganó la gobernación en enero de 1914 (Rojas, con Garro de vicegobernador). Es decir: las dos listas eran del régimen conservador (por eso van en el mismo bloque), pero solo la de Etchegaray era el oficialismo de 1912. La UCR no se presentó en San Juan en 1912 (Etcheverría). Pendiente: el debate de diplomas en el Diario de Sesiones 1912 (tomo I) y prensa sanjuanina de abril de 1912.
3. **Mendoza sale de un solo color** porque sus dos listas (Popular y Oficial) están en el bloque conservador. San Juan, idéntico (Oficial y Concentración Cívica): por eso va en sólido. La carpeta `busqueda1912` trae 107 mesas de San Juan en 32 colegios, pero sin asignar a departamentos (Barreal, Rodeo, Huaco, Astica, Cochagual, Pampa Vieja… no son departamentos) y con diferencias contra el resumen; **no se usaron**. Si se quiere ver Oficial contra Concentración hay que homologar los colegios y agregar un modo propio.
3b. **Unión Nacional gana** en Santiago del Estero y La Rioja (sólidas), 4 unidades departamentales (circunscripciones de Capital y un departamento de Córdoba) y no gana ninguna de Santa Fe.
4. **Participación nacional**: la Wikipedia imprime 73,20 %, pero 654.631 votantes sobre 935.001 inscriptos da **70,0 %** (las sumas provinciales de `PROV` cierran exactamente con ambos totales: el assert del build lo comprueba). El mapa muestra 70,01 %.
5. **Total de la tabla nacional (682.461)** suma votos de primeros candidatos y es la base de los %, por eso la torta dice «votos positivos» y la métrica «Votos a candidatos»; los votos válidos (electores) son 602.613. En Capital y Santa Fe los «votos a candidatos» superan a los votantes (panachage), y la participación provincial de esos dos usa el «total de votos» de la Wikipedia (Santa Fe: 78.345; el diario da 74.878 sufragantes).
6. **Capital**: el título de la tabla de Cantón dice 1912 pero el pie cita La Nación de 1916; las cinco columnas suman casi lo mismo que la Wikipedia 1912 (UCR 35.896 contra 35.721, UC 32.739 contra 32.749, PS 32.451 contra 32.512, UN 29.874 contra 29.825, Unión Comunal 17.096 contra 17.102), así que se trata como 1912. La columna 4 no tiene clave impresa y se rotula Socialista por una anotación manuscrita.
7. **Santa Fe** es prensa del escrutinio (anterior al diploma del 29/4; quedaban mesas complementarias del 21/4). Belgrano: la fuente repite a Valdez con 183 y 933; se usa Araya (183). Rosario: Coronado ilegible (es acompañante).
8. **Córdoba**: las cuatro columnas son listas y suman exactamente los votantes de cada departamento. La Wikipedia da otras cifras provinciales (máximo por candidato: Constitucional 23.582, UCR 15.690, UN 14.850) y no trae el Autonomista Nacional (10.876 en Cantón), que aquí se cuenta en conservadores.

## Pendientes

- Santa Fe: 14 departamentos (el diario *Santa Fe* del 16 al 25/4 tiene participación para los 19 y votos por candidato solo para 5); Córdoba: 5 filas sin cifra impresa.
- Tucumán (expediente 26-P-1912, 117 páginas) y las otras provincias sin cuadro departamental: ver `../busqueda1912/LEEME_1912.md`. Buenos Aires: el expediente solo da el total.
- Comparar los ganadores con el mapa vigente de Commons («Resultados por distrito.svg») no se hizo.
- Logos: UCR (bandera antigua bicolor) y PS (emblema); los demás llevan sigla.
