# Electorados provinciales: Sankey

**Ampliación del 2-nov-2026:** [búsqueda y empalmes por circuito](circuitos/LEEME.md), 27 cruces adicionales. El visor reúne 52 versiones: 2023 se amplía a nueve distritos, con nuevos circuitos para Chaco, Salta, Buenos Aires, CABA y Catamarca, y empalmes de municipios/distritos en Misiones y Santa Fe. En 2025 se agregan versiones más finas de Chaco, Corrientes, Misiones y Santa Fe. Se conservan las 25 versiones iniciales descritas abajo para comparar el efecto de la agregación.

Abrir `INDICE.html` o hacer doble clic en `abrir_sankey.cmd`. El visor y los datos están integrados en un HTML: no requiere servidor. Epilogue se carga de Google Fonts; sin conexión usa la fuente del sistema. El diseño sigue el tema Ink del explorador de Streamlit del usuario, con Hallmark (`.claude/skills/hallmark/SKILL.md`). No se desplegó ni modificó la aplicación pública.

## Alcance

25 cruces locales, con matrices, variantes, controles y exportaciones SVG/PNG/CSV:

| Serie | Cruces |
|---|---|
| Provinciales 2023 | Río Negro, Neuquén, Misiones y Salta: presidente 2019 → gobernador 2023; gobernador → presidente general 2023; gobernador → balotaje 2023 |
| Provinciales 2025 → diputados nacionales 26/10/2025 | Buenos Aires, CABA, Chaco, Corrientes, Jujuy, Misiones, Salta, San Luis y Santa Fe |
| Formosa 2025 | Pendiente: fuente oficial identificada, pero el servidor interrumpe las descargas. No se estimaron flujos |

Corrientes incluye gobernador, diputados y senadores por separado. Salta y San Luis separan las dos cámaras: no todos los departamentos eligen cada cargo y en San Luis Belgrano elige ambos. Buenos Aires usa el cargo legislativo provincial que correspondió a cada sección. Santa Fe es la elección general de **convencionales de distrito único del 13/04**, no las PASO municipales ni una elección de diputados. CABA elige legisladores porteños.

## Identidades preservadas

- Río Negro: JSRN propia y Nos Une Río Negro, ambas de Weretilneck, permanecen separadas (113.953 y 40.136 votos). JSRN no equivale a toda su coalición.
- Neuquén: MPN propio (lista 151), colectoras aliadas y Neuquinizate separados.
- Misiones: Frente Renovador de la Concordia, sin fusionarlo con fuerzas nacionales.
- Salta 2023: Gustavo Gobernador (Sáenz) y Avancemos (Estrada–Zapata) separados. Avancemos incluía a Ahora Patria: **el resultado de la alianza no permite aislar ese partido**.
- Buenos Aires 2025: Somos Buenos Aires y Potencia separados incluso por debajo del umbral de agrupación. No se asigna a una persona todo un frente.

2025 agrupa las listas menores al 2 % dentro del distrito como Otras listas, salvo las identidades destacadas. Las tablas provinciales originales conservan todas las fuerzas. El umbral nunca se calcula sobre el país.

## Cobertura y fuentes

Fuentes oficiales y archivos conservados con SHA-256 en `FUENTES.json`. Los resultados nacionales son el **provisorio DINE**, no un definitivo. Las provinciales son definitivas, salvo CABA, cuyo CSV es provisorio. Mezclar estados de escrutinio añade una limitación de comparabilidad.

| Cruce provincial de 2025 | Unidades utilizables | Reserva |
|---|---:|---|
| Buenos Aires | 135 municipios | Sólo positivos y blancos; el cuadro no publica nulos. Se recuperaron las páginas oficiales de San Miguel y Lezama omitidas en el índice |
| CABA | 167 circuitos | Mesas nativas, provisorio. Códigos coincidentes con octubre |
| Chaco | 25 departamentos | API del definitivo; todas las fuerzas y no positivos cierran exactamente con el total general |
| Corrientes | 25 departamentos | Esquina se suma desde Esquina y Pueblo Libertador. Diferencias internas entre agregado territorial y resumen de la API, conservadas sin ajuste |
| Jujuy | 139 circuitos | La fuente trae 149 y 369.394 positivos. Diez circuitos nacionales tienen cero votos informados: se excluyen de ambas bases. Cobertura provincial 99,814 % |
| Misiones | 17 departamentos | 78 tablas municipales de la publicación estadística oficial. Fracrán → Guaraní. Diferencias internas municipales/provinciales, sin ajuste |
| Salta, diputados | 209 subcircuitos | Cobertura provincial 99,615 %. Se excluyen resoluciones sin código, 46H/69A sin coincidencia y once códigos nacionales sin votos |
| Salta, senadores | 138 subcircuitos | Cobertura provincial 99,742 %. Se excluyen resoluciones sin código y siete códigos nacionales sin votos |
| San Luis, diputados/senadores | 5 / 4 departamentos | Cobertura completa de cada cargo. Muy pocas unidades para identificar flujos. Los porcentajes de cobertura nacional en el control se refieren a la provincia completa |
| Santa Fe | 19 departamentos | Columna Convencional Reformador Distrito Único del ODS oficial; suma 1.569.465 emitidos |

En Salta 2025 se comparan sólo válidos (positivos y blancos), porque la planilla provincial no incluye nulos. Los códigos se cotejan por subcircuito y se comprueba su pertenencia departamental para el denominador del cargo. Los caches nacionales por circuito se verifican al voto contra el agregado nacional por sección, que sólo contiene mesas nativas. Nunca se emparejan números de mesa entre elecciones distintas.

Misiones 2025: los 78 cuadros municipales cierran individualmente. Suman 555.879 emitidos frente a 555.868 del resumen publicado. Diferencias por fuerza (municipios menos resumen): PO −1, LLA −5, Por la Vida y los Valores −9, Libertario −3, FRC −22, Confluencia −1, Unidos por el Futuro +52; resto y no positivos sin diferencia. Se usan los valores territoriales impresos, sin completar residuos.

2023: Río Negro tiene 88 localidades, agrupadas a 13 departamentos administrativos (las ocho regiones llamadas Departamento en el portal son otra división). Neuquén tiene cinco circuitos rurales sin correspondencia (La Picaza, Paso Coihue, Quemquemtreu, Tralaitue, Zaina Yegua), excluidos; el control cuantifica su cobertura. Misiones usa 78 municipios y excluye 495 votos del personal asignado a centros publicados sólo en el total provincial. Se cotejaron celdas OCR contra imágenes; las correcciones están en `provinciales2023/preparar.py` y la lámina de revisión. Salta balotaje 2023 excluye Santa Victoria, sin votos nacionales informados: 22 departamentos, no 23.

Las correspondencias nominales se conservan en `provinciales2023/correspondencias_*.csv` y los alias en los scripts. Georef aporta localidades y departamentos; excepciones explícitas: Fachinal → Capital (Digesto de Misiones), Pozo Azul → San Pedro (ley XV-17), Pil Pil → Lácar (Boletín Oficial de Neuquén), Fracrán → Guaraní (estadística electoral oficial 2025, p. 23). Río Negro, Lonco Vaca–Aguada Guzmán se asigna por Aguada Guzmán a El Cuy según la región electoral; no por el topónimo homónimo de Georef en Valcheta. No hay coincidencias difusas automáticas.

## Qué significa el ancho

Inferencia ecológica RxC, usando el port de Calvo del proyecto. Se estima cada provincia por separado, sin prior nacional. Se ajusta `Y ≈ X B`: X e Y son las composiciones territoriales y B tiene filas no negativas que suman uno.

La variante principal pondera por el volumen territorial de destino y elige penalización entre 10⁻³ y 10⁻⁷ con validación cruzada determinista. Se compara con la variante sin pesos de Calvo, penalización 0,001. Se conserva su pérdida sobre C−1 categorías; en 2025 la categoría de referencia se coloca explícitamente al final (blanco o blanco y nulo). No hay raking ni ajuste posterior de los márgenes.

El ancho de una fila es `Σterritorios(proporción de origen × base territorial de destino)`, multiplicado por su fila de B. Es una cantidad **equivalente en la base de destino**, no votos originales ni personas observadas. Los márgenes derechos son modelados y pueden diferir de los observados, que se publican aparte y se comparan en la tabla. Invertir la lectura condiciona la matriz conjunta por columna; no equivale a estimar otro modelo.

Sólo Río Negro y Salta 2023 incluyen No votó con padrón provincial verificado. Neuquén y Misiones 2023 usan emitidos. En Misiones el padrón municipal incluye extranjeros y no permite una abstención comparable. Los cruces de 2025 omiten abstención: no deben interpretarse como entradas y salidas de votantes ni permiten separar movilización de cambio de fuerza.

## Incertidumbre

200 remuestreos territoriales (semillas 1100–1299), percentiles 5–95. No son intervalos que cubran todos los sesgos. También se evalúan todas las penalizaciones y la eliminación de una unidad.

Se marca una fila con asterisco si: diferencia máxima entre variantes >30 pp (o >20 pp en filas menores al 5 %); ancho máximo de percentiles >40 pp; rango de X inferior al número de orígenes; menos de `max(10, 2R)` unidades; o sensibilidad >35 pp. Es un diagnóstico conservador, no una validación individual. En San Luis todas las filas quedan marcadas. Varios cruces de 2023 también tienen poca identificación: no autorizan afirmar que una fuerza sea pro LLA o kirchnerista a partir de la estimación puntual.

## Reproducir

Desde la raíz, Python 3.11 con numpy, pandas, scipy, lxml, PyMuPDF, pdfplumber y openpyxl. Los originales descargados permanecen en las dos carpetas `fuentes/`; algunas rutas oficiales pueden dejar de responder.

```powershell
python -X utf8 transferencias/provinciales2023/preparar.py
python -X utf8 transferencias/provinciales2023/construir_bases.py
python -X utf8 transferencias/provinciales2025/preparar.py
python -X utf8 transferencias/provinciales2025/chaco.py
python -X utf8 transferencias/provinciales2025/corrientes.py
python -X utf8 transferencias/provinciales2025/misiones_estadisticas.py
python -X utf8 transferencias/provinciales2025/extras.py
python -X utf8 transferencias/provinciales2025/construir_bases.py
python -X utf8 transferencias/provinciales/estudio.py
python -X utf8 transferencias/provinciales/construir_visor.py
python -X utf8 transferencias/provinciales/catalogar_fuentes.py
python -X utf8 transferencias/provinciales/verificar.py
```

`estudio.py` invalida su caché por datos, configuración y código del estimador. `construir_visor.py` integra estilo y datos. `verificar.py` coteja datos, conservación, no negatividad, 25 selectores, ambas variantes, perfiles de origen/destino y descargas reales en Edge; exporta todos los SVG/PNG y `VALIDACION.json`. No ejecuta el modelo de nuevo.

## Diseño y revisión

Sistema Ink tomado de `.streamlit/config.toml` y `transferencias/explorador/index.html`; fuente Epilogue y superficies de papel. Los colores partidarios no son la paleta de la interfaz. Hallmark se aplica a la pantalla de análisis, sin portada publicitaria. Estilo en `estilo.css`, tokens y base separados, integrados para el HTML final. Los perfiles se apilan como registros en celular; el gráfico tiene un área de desplazamiento horizontal con etiqueta accesible.

La aplicación pública de referencia fue capturada con `capture.mjs`. La revisión visual y de Hallmark se registra en `.hallmark/`; el control numérico es independiente. No se ha publicado esta nueva serie.

Revisión final: los 25 cruces conservan sus bases, matrices estocásticas y masa equivalente; ambas variantes, perfiles de origen/destino y descargas reales funcionan. Etiquetas sin desbordes ni solapes. Hallmark: 0 FAIL, 0 REFLEX, 0 WARN; cuatro ocurrencias de la excepción documentada del tema Ink para neutros sin tono. Revisión visual en la misma conversación, con dos ajustes resueltos (siglas/nombres y separación de etiquetas). No hubo revisión por un segundo agente.
