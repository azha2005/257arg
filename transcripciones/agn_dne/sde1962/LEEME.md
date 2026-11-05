# Santiago del Estero, diputados nacionales, 18 de marzo de 1962

**Fuente**: Archivo General de la Nación, Departamento Archivo Intermedio, fondo Dirección Nacional Electoral, serie
Resultados, carpeta `AR-AGN-DNE01-De-re-29_056_246a273` (28 imágenes TIF que mandó el AGN el 5-nov-2026; copia local
del usuario en `C:\Users\JC\Downloads\agn\29_056_246a273\`, fuera de git). Planilla manuscrita «Elección - fecha:
Dip. Nac. 18-III-62, Distrito: S. del Estero», hojas 1 a 5 (folios 247-251 = imágenes 0002-0006). Las imágenes 0007-0011
son una segunda copia idéntica; las demás son la nota del Juzgado Electoral (27-jun-1962) y el acta general de la Junta
Electoral Nacional con resultados provinciales y municipales por circuito (no transcriptos).

**Transcripción**: `sde1962.csv`, una fila por departamento (27) más la fila «TOTAL GENERAL» de la hoja 5, que es solo
control. Votos de cada partido, en blanco, anulados, votantes y electores hábiles. Los «-» del original son 0. No se
transcribieron los porcentajes, pero se usaron para controlar.

Partidos tal como los escribe la planilla: Autonomista (Partido Autonomista de Santiago del Estero), Blanco (Partido
Blanco, neoperonista: **no** son votos en blanco, que van en «En blanco»), Conservador Popular, Demócrata Nacional,
Demócrata Cristiano, Movimiento Radical Popular, Socialista, UCRI, UCR de Santiago del Estero y Tres Banderas.

**Controles** (`python transcripciones/agn_dne/agn.py`):
- Todos los departamentos cierran: partidos + en blanco + anulados = votantes.
- Cada columna suma el total general de la planilla, que coincide con la tabla de la Wikipedia en todos los partidos
  (Tres Banderas 68.279, MRP 56.057, UCRI 50.392…) y con los votantes (193.530).
- **Única diferencia**: los electores hábiles de los departamentos suman 283.351 y el total de la planilla (y la Wikipedia)
  dice 283.251. Las dos copias dicen lo mismo y los porcentajes de participación escritos para cada departamento coinciden
  con las cifras transcriptas (ninguno coincide si se le restan 100), así que es un error de suma del original. Se deja cada
  departamento como está escrito.
- «La Banda» se carga como «Banda», el nombre que usa Cantón en 1958 y 1965. Matará es Juan Felipe Ibarra en el mapa de 1960.

**Uso**: `transcripciones/agn_dne/agn.py` la convierte al formato de las páginas de Cantón y `canton5865/cargar.py` la suma;
el atlas 1962 (`python transcripciones/canton5865/atlas5865.py 1962`) ya no pinta la provincia en color sólido.
