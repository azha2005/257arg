# Continuación: provincias competitivas

Consulta: 15/10/2026. Prioridad indicada por el usuario: concentrar esfuerzo en provincias competitivas y relegar **Tucumán**, al que se refería la aclaración sobre falta de oposición. El inventario tucumano se conserva; no se incorporan nuevas cifras tucumanas en esta tanda.

## San Juan: ampliación y segunda lectura

Se transcribieron visualmente las actas del 27-D, PDF 5-78, y se leyó el resumen/fundamentación de PDF 81-89. El registro tiene **107 posiciones de mesa y 428 cifras de los cuatro candidatos principales**, agregadas en **32 rótulos territoriales literales / 128 filas** del CSV principal. La fuente declara 107 mesas, pero la coincidencia del conteo no certifica por sí sola la homologación de cada localidad a un departamento histórico. Albardón registra conjuntamente la quinta mesa y su fracción.

| Candidato | Suma de cifras expresas por mesa | Resumen provincial PDF 82 | Diferencia |
|---|---:|---:|---:|
| Augusto Echegaray | 8.850 | 8.853 | -3 |
| Estanislao Albarracín | 8.760 | 8.759 | +1 |
| Luis R. Brandam | 8.526 | 8.506 | +20 |
| Pedro A. Garro | 8.607 | 8.593 | +14 |

**No es todavía una certificación del resultado final por mesa.** PDF 85 declara que la Junta eliminó al azar o consideró blancos diferencias entre sobres y actas de mesas reservadas, y remite a un acta adjunta. Falta localizar esa distribución y cotejar las diferencias restantes. No se fuerza la suma a los totales provinciales. Los votos dispersos aún no se transcribieron exhaustivamente: la tabla cubre los cuatro candidatos principales.

Correcciones documentadas de esta pasada:

- Iglesia tiene dos mesas (PDF 48); las siguientes, de PDF 49, pertenecen a **Rodeo**, que tiene tres. Se corrigió una asignación territorial inicial y se añadió Iglesia 2.
- Rivadavia 3 dice **veintisiete** para Echegaray y Albarracín (PDF 35, recorte `san_juan_rivadavia3_detalle2.png`); no 97.
- Pocito 6 complementaria da **63** a cada candidato opositor (PDF 78, recorte `san_juan_pocito6_detalle2.png`); no 73.
- PDF 82 dice **8.593** para Garro, no 8.533 (`san_juan_provincial_detalle2.png`). El nombre Garro se había leído erróneamente Cano; queda corregido en las tablas. Echegaray/Etchegaray y Brandam/Brandan mantienen reserva de grafía.
- Mogna complementaria: 136/136/27/27, PDF 76-77; Calingasta: 123/121/79/84, PDF 77; Pocito 6: 115/115/63/63, PDF 77-78. Las tres corresponden al **21/4**, escrutadas el **24/4**. No se suman a originales anulados.
- Caucete 3 y 25 de Mayo 1 fueron reservadas y luego admitidas/escrutadas (PDF 73-75); permanecen fechadas 7/4.

Archivos reproducibles: `san_juan_mesas_candidatos.csv`, `san_juan_mesas_controles.csv`, `san_juan_cotejo_provincial.json`. En algunos registros sólo se expresan votos de candidatos; sufragantes y blancos ausentes siguen vacíos. El control condicional de dos votos por sufragante no es un cálculo de blancos ni una certificación de la semántica de cada mención manuscrita.

## Santa Fe: cotejo nominal y límites de los diarios

El diploma de 29/4, 17-D PDF 3, confirma Araya **36.747**, Ávalos **36.513**, Coronado **36.147**, Valdez **35.855**, Pesenti **17.856** y de la Torre **17.630**. Se comparan ahora contra los mismos candidatos del diario 25/4 en `santa_fe_cotejo_diploma.csv`. La comparación anterior del máximo radical del diario contra el máximo de Wikipedia no era un cotejo del mismo candidato: se retiró como medida de discrepancia nominal.

La crónica del 25/4 es anterior al cierre de la Junta del **26/4** (PDF 30) y al diploma del 29/4, aunque anuncia resultados tras complementarias. No reemplaza el resultado aceptado. La disminución de Fernández entre dos crónicas sigue sin resolver.

PDF 27 localiza mesas anuladas y convocatoria para el 21/4, incluidas mesas de departamentos ya transcritos. Las cinco tablas departamentales de diarios no se certifican como definitivas por esta revisión. Las lecturas inseguras de Coronado/Rosario y Casablanca/San Lorenzo siguen vacías: las ampliaciones del mismo zoom no aportan resolución adicional. El nivel público 5 devuelve una respuesta de archivo inexistente, no una imagen.

El cuadro departamental del 24/4 p. 1 (6513) corresponde expresamente al **31 de marzo, elección provincial**; descartado para diputados nacionales. Véase `SANTA_FE_PISTAS_NUEVAS.md`.

## Mendoza: reserva acotada, sin absorber más esfuerzo

Se volvió a comprobar PDF 103/105: la enumeración final omite San Martín 7 y el resumen imprime 74 votos dispersos. Siguen 70 recuperados, diferencia -4. No se completaron por residuo Lavalle 9/Benegas ni Maipú 14/Gaviola.

Se localizó otro tomo de DSCD 1912, volumen I, Google Books **VrxHAQAAMAAJ**. Búsquedas internas ubican dictamen y aprobación de Mendoza en **p. 110**, y discusión general en pp. 8-11. Las respuestas están en `fuentes/dscd_1912_*.json` y el registro en `fuentes/dscd_consultas.csv`. El endpoint público de imagen de PA110 respondió HTTP 200 con el cartel **image not available** (`dscd1912_PA110.jpg`): no se registra como página del Diario recuperada. Los fragmentos de búsqueda no sirven para llenar cifras. [Localizador de p. 110](https://books.google.com/books?id=VrxHAQAAMAAJ&pg=PA110).

## Próximo trabajo útil

1. San Juan: localizar el acta de ajuste mencionada en PDF 85 o el escrutinio parlamentario; cotejar las cuatro diferencias y después homologar colegios/localidades históricas. La fuente ofrece competencia provincial muy estrecha: 8.853 frente a 8.593 para los candidatos más votados de cada agrupación.
2. Santa Fe: actas parciales y diarios del escrutinio nacional de mediados de abril; priorizar departamentos sin cifras y no los cuadros de marzo provincial. Mantener separadas complementarias y resultados iniciales.
3. Córdoba/Capital: buscar una segunda fuente que resuelva respectivamente departamentos sin cifra y la reserva de fecha de Cantón; Buenos Aires: actas parciales/anuarios, porque el expediente corto sólo da la provincia.
4. Tucumán permanece en segundo plano por decisión del usuario. Mendoza conserva sus reservas precisas; no gastar nuevas rondas en los cuatro votos dispersos mientras haya provincias competitivas sin cobertura.

La base principal queda en **477 filas: 450 numéricas y 27 vacías**. La cantidad mide registros recuperados, no votos certificados ni cobertura nacional. No se modificaron atlas.
