# Auditoría de continuidad de fase 2

Fecha: 15 de octubre de 2026. Alcance: inventario de `LEEME_1914.md`, `consolidar.py` y `busqueda1914/fase2/`. No se transcribieron cifras electorales ni se abrieron teselas individuales de prensa. Se inspeccionaron nombres, formatos, manifiestos, informes y la lógica de los scripts.

> **Vigencia:** el cuerpo de este documento es un snapshot anterior a la integración de fase 2; sus hallazgos históricos se conservan sin cambios. Después de ese corte, el consolidado incorporó Córdoba principal más complementarias y el agregado de La Rioja, y `fuentes.csv` pasó a incluir registros de fase 2. El conteo de 1.043 filas de las 02:28 fue un corte intermedio. El control estructural actualizado, medido el 15/10/2026 a las 02:31:57 (-03), registra 1.192 filas principales (1.094 con `votos`, 98 vacías) en siete distritos, además de 120 filas parciales mantenidas aparte. Mendoza aporta 149 filas al principal y su complementaria de 46 filas sigue separada. Ver `CONTROL_INTEGRACION.md` para el desglose, las claves y las referencias. Este corte tampoco certifica las transcripciones y puede quedar desactualizado con nuevas integraciones.

## Estado previo al integrar fase 2

El consolidado vigente contiene 974 filas: 874 cifras y 100 ausencias explícitas, en Buenos Aires, Capital Federal, Córdoba, Corrientes y Entre Ríos. Córdoba representa la elección principal y deja las complementarias aparte. `datos_1914_canton_comparacion.csv` es una transcripción comparativa separada, no otra capa que se sume al consolidado.

`consolidar.py` vuelve a generar `datos_1914_depto.csv`, `datos_1914_canton_comparacion.csv`, `fuentes.csv`, `inventario_pdfs.csv` y `control_consolidacion.json`. Para el consolidado principal selecciona Cantón de `partes/`, la tabla primaria de `partes/cordoba_hcdn/datos.csv` y Corrientes de `partes/corrientes/datos.csv`. Mantiene expresamente fuera las variantes del resumen cordobés y las mesas objetadas de Jujuy. Sus entradas de fuentes son `fuentes_hcdn.csv`, `fuentes_alternativas.csv` y los manifiestos de `partes/*/`; no recorre `fase2/`.

Los controles de ese script cubren columnas requeridas, votos enteros, referencia y fuente presentes, clave de fila sin duplicados y correspondencia de cada `fuente_id` con el manifiesto. El inventario abre los PDF y registra páginas, hash e integridad de lectura. Esos controles estructurales no prueban que las sumas electorales cierren.

La última actualización del informe y los productos principales precede a los productos derivados que ahora hay en fase 2. `LEEME_1914.md` todavía describe Córdoba como pendiente de integrar las complementarias y La Rioja como pendiente de transcripción/agregado. Por eso el informe no representa ya el estado completo del árbol.

## Inventario resumido de fase 2

| Distrito | Qué hay | Estado de integración y control |
|---|---|---|
| Córdoba | `combinar.py`, `datos_principal_mas_complementaria.csv`, `variante_resumen_mas_complementaria.csv`, correspondencias, componentes, adiciones posteriores sin departamento, totales publicados y controles. | No entra al consolidado. El producto detallado principal más complementaria y la variante derivada del resumen son dos representaciones alternativas de parte de la misma elección; `controles_finales.csv` conserva discrepancias y advierte que los votos posteriores sin departamento no se reparten. |
| La Rioja | `generar_la_rioja.py`, `datos_mesa.csv` y `datos.csv`, además de imágenes de páginas del expediente. El script separa filas declaradas válidas y anuladas; `datos.csv` agrega las válidas por departamento y candidato. | El CSV agregado ya usa el esquema largo del consolidado, pero aún no se incorpora. El manifiesto principal identifica el mismo expediente con `fuente_id=13-p-1914` y estado anterior a inspección; el generador usa `HCDN_13-P-1914`. Hay que reconciliar la identidad, localizadores y estado. El script imprime sumas, pero no genera un informe de control independiente ni tiene aserciones de cierre. |
| Santa Fe | Descargas de prensa con teselas, mosaicos de página, HTML, OCR parcial y CSV de estado de descargas. `prensa.py` registra solicitudes y arma mosaicos. | No hay todavía un conjunto largo departamental ni un control electoral dentro de esta carpeta. Los registros de descarga son evidencia de obtención, no resultados transcritos ni conciliados. No se inspeccionaron las teselas en esta auditoría. |
| Mendoza | No hay subcarpeta en `fase2/`. | `LEEME_1914.md` indica que se recuperó el expediente territorial, pero sigue pendiente transcribirlo y agregarlo. No hay salida nueva que integrar desde fase 2. |
| Tucumán | Páginas del Diario de Sesiones recuperadas como imágenes/HTML, manifiestos de contexto y expedientes APyM descargados, con scripts de búsqueda/recuperación. | No hay CSV electoral ni informe provincial. Los manifiestos indican contenido por inspeccionar o identidad pendiente; los identificadores del catálogo no deben asignarse a Tucumán hasta confirmar el distrito y el comicio en el documento. |
| Jujuy | Dos expedientes APyM identificados, PDF/TXT y recortes de páginas. | No hay CSV de resultados ni informe de verificación; ambos registros de fuente dejan pendiente confirmar identidad. Mantener aparte de las cifras de mesas objetadas de la fase 1. |
| Entre Ríos | `informe.md`, `fuentes.csv`, descargas APyM/prensa/bibliografía y `datos.csv` con solo encabezado. | El informe documenta una búsqueda negativa acotada y cero cifras nuevas comprobadas; no aporta filas electorales para agregar. El expediente catalogado como entrerriano `24-P-1914` corresponde en el PDF a Santa Fe. |

La carpeta no tiene un agregador común de fase 2. Los únicos scripts con salidas de datos integrables son `cordoba/combinar.py` y `la_rioja/generar_la_rioja.py`; los scripts restantes buscan, descargan, registran o renderizan fuentes.

## Riesgos de duplicación o atribución

- **Córdoba:** anexar `datos_principal_mas_complementaria.csv` a las filas cordobesas actuales duplicaría la elección principal. Para actualizar Córdoba hay que reemplazar todas sus filas seleccionadas por una sola versión canónica. No mezclar esa salida con `variante_resumen_mas_complementaria.csv`, `componentes_complementaria.csv`, `correspondencia_complementaria.csv` ni con los totales provinciales: son variantes, trazas de emparejamiento o controles, no bloques adicionales de departamentos.
- **Córdoba:** `adiciones_posteriores_sin_departamento.csv` no puede repartirse entre unidades. La nota de los controles distingue esos totales de la suma territorial; conservarlos como evidencia separada.
- **La Rioja:** `datos_mesa.csv` y `datos.csv` representan los mismos votos a distinto nivel. Importar ambos duplica resultados. La salida agregada separa del consolidado las mesas anuladas; preservar además el detalle por mesa como respaldo. Una candidatura ausente no debe transformarse en cero.
- **Jujuy:** las cifras propuestas para anulación en fase 1 no son resultados válidos completos. Los nuevos expedientes sin identidad confirmada no justifican sumarlas ni sustituirlas.
- **Santa Fe:** no convertir el registro de teselas, el OCR parcial o una transcripción de una página en escrutinio completo. Mantener el localizador por página y distinguir tablas parciales por localidad/candidato de un total departamental verificado.
- **Tucumán:** los expedientes hallados por búsqueda de catálogo pueden pertenecer a otra provincia o elección. Verificar portada, localidad, fecha y alcance antes de asociarles cifras o fusionar su fuente con el identificador de otro distrito.
- **Fuentes comunes:** la comparación de Cantón ya duplica territorios incluidos en el archivo principal, con otra unidad de observación. Seguir manteniéndola separada. Los totales de candidatos/listas tampoco se deben sumar como si fueran electores ni armonizar por residuo.
- **Manifiestos:** los `fuente_id` de fase 2 no siempre coinciden con los del manifiesto principal, aunque apunten al mismo PDF. Deduplicar por identidad documental verificada y registrar como fuentes distintas los productos derivados, con su original y localizador.

## Plan concreto de integración

1. **Córdoba:** adoptar como candidata principal la salida detallada `datos_principal_mas_complementaria.csv`, reemplazando —no anexando— la selección cordobesa actual. Mantener la variante basada en el resumen y las adiciones sin departamento fuera de `datos_1914_depto.csv`, enlazadas desde `fuentes.csv` y descritas en el informe. Antes de regenerar, resolver desde `controles_finales.csv` cada diferencia entre el detalle, la variante y los totales generales; conservar las discrepancias no resueltas sin corregir por residuo.
2. **La Rioja:** revisar la correspondencia de los rótulos del agregado con la fuente y su alcance, cotejar los controles por mesa/departamento/candidato con el expediente y conservar los casos incompletos/anulados. Después añadir solo `datos.csv` al conjunto seleccionado. Unificar `HCDN_13-P-1914` con el registro existente `13-p-1914` o documentar por qué son fuentes distintas; actualizar archivo, páginas, método y estado de verificación en el manifiesto.
3. **Fuentes en progreso:** actualizar Entre Ríos en `LEEME_1914.md` con su informe de búsqueda y sin agregar filas. Para Santa Fe, Tucumán y Jujuy, incorporar registros de fuente a la salida consolidada solo después de verificar identidad y localizador; agregar filas únicamente tras transcripción y control aritmético. Dejar las búsquedas negativas como hallazgos documentales, no como datos.
4. **Consolidación reproducible:** ampliar `consolidar.py` con una lista explícita y documentada de entradas fase 2, normalización de `fuente_id`, controles por distrito y reglas de exclusión. Mantener el CSV comparativo de Cantón separado. Regenerar una sola vez `datos_1914_depto.csv`, `fuentes.csv`, `inventario_pdfs.csv` y `control_consolidacion.json` desde esa selección.
5. **Cierre documental:** actualizar `LEEME_1914.md` después de las salidas y controles; distinguir qué está integrado, qué está solo descargado y qué quedó pendiente. No tocar mapas ni construir atlas: el prompt limita este trabajo a búsqueda y datos.

## Límites de esta auditoría

Se verificó estructura y presencia de artefactos, referencias de los scripts y controles declarados. No se ejecutaron generadores, no se recalcularon cifras y no se comprobó visualmente cada página del expediente o la prensa. La existencia de un CSV generado acredita que el script produjo una salida, no que la transcripción sea correcta.

## Nota posterior al snapshot

Tras el corte descrito en el cuerpo, `consolidar.py` fue actualizado para sustituir las filas cordobesas por `fase2/cordoba/datos_principal_mas_complementaria.csv`, agregar `fase2/la_rioja/datos.csv` y recoger manifiestos de fase 2. La auditoría de estructura, claves, referencias y archivos del consolidado resultante queda en `CONTROL_INTEGRACION.md`; no modifica ni reemplaza los hallazgos históricos de este documento.
