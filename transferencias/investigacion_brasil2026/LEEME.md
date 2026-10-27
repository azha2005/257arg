# Brasil 2026: fuentes y adaptación de transferencias

Investigación del 26-oct-2026 (Argentina). Alcance principal: presidente, primera vuelta del 4 de octubre → balotaje del 25 de octubre. También se identifica el camino para gobernadores y cruces con legislativas.

**Implementado y calculado tras la autorización del usuario:** [informe, matrices, auditoría y controles](../brasil_2026p_2026b/RESUMEN.md) y [Sankey con selector de UF](../brasil_2026p_2026b/sankey_brasil_2026p_2026b.html). La investigación que sigue describe la propuesta inicial; las decisiones finales están en el informe (incluida la tolerancia acotada de padrón y su sensibilidad estricta). Revisión del 26-oct-2026: matrices por región geográfica del IBGE encogidas hacia su UF, prueba fuera de muestra, bootstrap que recalcula centro y penalizaciones, alerta de celdas en el borde y sankey del proyecto (`sankey.py`).

## Hallazgo verificado

El TSE tiene disponibles votos presidenciales y detalle de participación **por sección electoral**, con registros de ambos turnos. Se verificaron cabeceras y muestras de los CSV dentro de los ZIP mediante HTTP Range, sin descargar archivos completos. Esto verifica disponibilidad y esquema, no cobertura nacional completa ni carácter definitivo de cada totalización.

- Catálogo: https://dadosabertos.tse.jus.br/dataset/resultados-2026
- API del catálogo: https://dadosabertos.tse.jus.br/api/3/action/package_show?id=resultados-2026
- Presidenciales: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip
- Detalle de participación: https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip
- Alternativa agregada, votos nominales: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip
- Alternativa agregada, detalle: https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2026.zip
- Boletines de urna: https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna
- Documentación de divulgación JSON/JWS: https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/divulgacao-de-resultados

El catálogo también enlaza ZIP de votación por sección para cada UF, útiles para gobernadores y legisladores. Para presidente, comenzar por BR; inspeccionar si contiene registros SG_UF=ZZ antes de afirmar cobertura del exterior. No sumar BR a los archivos estatales sin verificar solapamientos. En el ZIP de detalle, el miembro BR contiene presidente; el miembro ZZ observado solo tenía cabecera, lo cual no prueba que no haya exterior dentro de BR.

## Descarga y versión: incidencia real

Durante el sondeo, HEAD de presidenciales informó 241.891.087 bytes y Last-Modified 26-oct-2026 17:42:32 GMT, pero GET Range de la URL canónica devolvió una versión de 161.616.519 bytes del 6 de octubre. No mezclar fragmentos de esas versiones.

La consulta con `?verificacion=20261026` devolvió la versión del 26 de octubre, con un CSV de 1.578.545.088 bytes descomprimidos. En una muestra acotada se observaron NR_TURNO=1 / CD_ELEICAO=6257 / DT_ELEICAO=04/10/2026 y NR_TURNO=2 / CD_ELEICAO=6258 / DT_ELEICAO=25/10/2026. Los identificadores se comprobaron en el CSV; no son constantes que deban extrapolarse a otros años o cargos.

El ZIP de detalle observado mide 234.357.769 bytes y se modificó el 26 de octubre. Su CSV BR también mostró ambos turnos de presidente.

Conservar URL efectiva, fecha de descarga, ETag, Last-Modified, SHA256 del ZIP completo y DT_GERACAO/HH_GERACAO de los datos. Comprobar turnos presentes y consistencia de los totales después de descargar. Un cambio de query resolvió esta respuesta antigua, pero no garantiza futuras actualizaciones.

Evidencia reproducible: `sondeo_tse.json`, `sondeo_presidente_consulta.json` y `sondear_tse.py`. El último sondeo presidencial transfirió aproximadamente 82 KB. El script general usa URLs canónicas y puede volver a observar la versión antigua; la consulta diferenciada está registrada en el segundo JSON.

## Esquema de entrada observado

CSV con separador `;`, campos entre comillas y texto legible con Latin-1 en las muestras. Procesar por chunks y validar la codificación con el leiame del paquete antes de la carga completa.

Clave territorial propuesta: `(SG_UF, CD_MUNICIPIO, NR_ZONA, NR_SECAO)`. Mantener códigos como texto. `NR_TURNO`, `CD_ELEICAO`, `DT_ELEICAO` y `CD_CARGO` identifican la observación electoral y se filtran antes de pivotar; el turno no forma parte de la clave usada para emparejar ambas vueltas.

Votos: `CD_CARGO=1`, `DS_CARGO=Presidente`, `NR_VOTAVEL`, `NM_VOTAVEL`, `SQ_CANDIDATO`, `QT_VOTOS`. La muestra del segundo turno incluye `NR_VOTAVEL=96`, `NM_VOTAVEL=VOTO NULO`. Validar todos los códigos especiales con el diccionario y los nombres; no tratar cada NR_VOTAVEL como candidato. Guardar candidatos individualmente antes de cualquier agrupación analítica.

Detalle: `QT_APTOS`, `QT_COMPARECIMENTO`, `QT_ABSTENCOES`, `QT_VOTOS_NOMINAIS`, `QT_VOTOS_BRANCOS`, `QT_VOTOS_NULOS`, `QT_VOTOS_LEGENDA`, `QT_VOTOS_ANULADOS_APU_SEP`, `ST_SECAO_INSTALADA`, `ST_SECAO_ANULADA`, `DS_ORIGEM_VOTO`; también `NR_LOCAL_VOTACAO` y dirección del local.

Filtrar presidente en el detalle y tomar sus aptos una sola vez por sección/turno. El archivo incluye varios cargos: sumar QT_APTOS por filas duplicaría electores. Los blancos y nulos se pueden leer de detalle o votos, pero nunca sumar ambas representaciones.

## Adaptación al algoritmo actual

Revisados `transferencias/LEEME.md`, `estimar.py`, `rxc_calvo.py`, `auditar.py` y `sankey.py`. El núcleo es RxC por mínimos cuadrados penalizados con matriz de transición softmax. La implementación principal ajusta un centro nacional ponderado y matrices provinciales penalizadas hacia ese centro; compara una variante nacional Calvo y usa validación cruzada y bootstrap.

1. Crear un adaptador brasileño que produzca tablas A y B por sección con las mismas unidades comparables. Origen: todos los candidatos de primera vuelta, blancos/nulos y abstención. Destino: los dos finalistas, blancos/nulos y abstención. Se pueden separar blancos y nulos en una variante si la señal permite estimarlos; categorías pequeñas requieren auditoría.
2. Construir abstención con QT_ABSTENCOES; comprobar `aptos = comparecimiento + abstenciones` y el cierre de votos del cargo contra comparecimiento, documentando separadamente anulados/sub judice/casos especiales según diccionario. No convertir residuos desconocidos automáticamente en abstención.
3. Emparejar secciones y comparar aptos entre turnos. Investigar agregaciones, transferencias temporarias, secciones ausentes/anuladas y cambios de local. Cuando exista correspondencia documentada, sumar ambos lados al mismo grupo; si no, excluir y reportar cobertura. Un cambio de dirección solo no prueba que cambió el conjunto de electores. No aplicar automáticamente el filtro argentino de padrón -25/+33 %: entre vueltas del mismo año corresponde un control más estricto, calibrado a los datos.
4. Normalizar por QT_APTOS: X=A/N1 y Y=B/N2. Mantener «No votó» dentro del ajuste aunque luego se reduzca visualmente en el Sankey. Si N1=N2 por sección, la masa de origen no necesita el reescalado de padrón que usa el modelo entre años; cualquier discrepancia exige explicación.
5. Reutilizar `rxc_calvo.fit` y la lógica de ajuste nacional/territorial, sustituyendo provincias argentinas por las 27 UFs. Exterior por separado, cuando se verifique su cobertura. Reestimar lambda: no trasladar 2e-6 ni 2e-7 de otros pares.
6. Para Brasil, agrupar folds de validación por municipio o local de votación; remuestrear bloques de locales/municipios dentro de cada UF en vez de secciones independientes. Las secciones del mismo local están relacionadas. Comparar resultados por sección, por local y por municipio/zona; mayor granularidad no garantiza identificación ni intervalos pequeños válidos.
7. Conservar comparación principal/Calvo y las alertas por filas pequeñas, filas próximas al promedio y sensibilidad al modelo. Ejecutar además controles de estabilidad por escala territorial. El bootstrap actual mantiene fijo el centro nacional: explicitar esa limitación o recalcularlo en cada réplica si se busca incorporar su incertidumbre.
8. Auditar predicciones por unidad usando SU matriz de UF, además de marginales nacionales y estatales. El RMSE final actual de estimar.py aplica una matriz nacional agregada: no basta para evaluar el ajuste territorial. El método no impone cierre exacto de las marginales de destino; reportar desvíos, y si se agrega calibración a marginales, entregar la versión original y explicar el procedimiento separado.

No basta agregar dos entradas en CAT y ejecutar estimar.py: `prepare` incorpora correspondencias argentinas, conversiones de año, tablas de secciones locales y reglas de Capital; el Sankey tiene nombres de distritos, títulos y etiquetas de circuitos argentinos. Conviene un wrapper de Brasil con configuración territorial propia y el mismo núcleo, preservando los cruces existentes.

Salidas propuestas en `transferencias/brasil_2026p_2026b/`: matriz_votos.csv, matriz_pct.csv, por_uf.csv, calvo_nacional.csv, intervalos.csv, control.json, correspondencias/exclusiones y Sankey nacional con selector de UF. Son rutas propuestas, todavía no generadas.

## Otros cargos y límites

- Gobernador: repetir por estado solo donde efectivamente hubo segundo turno, usando sus candidatos y turnos. No mezclar como si fueran los mismos candidatos nacionales.
- Diputados → presidente: posible cruce de elecciones simultáneas, agrupando votos nominales y de legenda por partido/federación con metadatos oficiales. Es asociación entre decisiones para cargos, no cambio temporal entre vueltas.
- Senado: no usar directamente una fila de votos como si fuera una persona. La muestra de 2026 tiene secciones donde los votos senatoriales superan comparecimiento; un modelo de una opción por elector requiere otra definición de unidad/categoría.
- El catálogo advierte 39 registros duplicados asociados a transferencias temporarias: 158.745.502 registros frente a 158.745.463 electores efectivos. Verificar su localización y tratamiento oficial; no restar 39 arbitrariamente a una sección.
- Usar TSE como autoridad para los marginales de este estudio. La regla Wikipedia del proyecto se refiere al topline de los atlas; no justifica sustituir las marginales observadas usadas para inferencia.
- Una matriz estimada no observa personas ni permite afirmar transferencias individuales exactas. Filas pequeñas o correlacionadas pueden quedar sin identificar aunque haya muchas secciones. No imponer que los votantes de los finalistas permanezcan en su candidato, ni interpretar toda ganancia como proveniente de candidatos eliminados.

## Secuencia de implementación recomendada

Descarga completa y hashes → inspección de leiame → carga presidencial en chunks y validación de ambos turnos → emparejamiento y cobertura por UF → piloto de una UF → matriz nacional/UF con selección de penalización → sensibilidad territorial y bootstrap por bloques → auditoría y Sankey. La disponibilidad quedó verificada; el ajuste y la validación completa de las bases quedan pendientes de implementación.
