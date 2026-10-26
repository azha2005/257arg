# Ampliación de las pistas prometedoras, 15/10/2026

**Este informe conserva la primera ampliación. Estado posterior y prioridad vigente: [PROGRESO_COMPETITIVAS_1912.md](PROGRESO_COMPETITIVAS_1912.md).** San Juan ya se amplió a 107 registros; Tucumán quedó relegado por decisión del usuario. Las lecturas iniciales Cano/8.533 fueron corregidas a Garro/8.593 en la nueva revisión.

Se revisaron visualmente las páginas sustantivas del expediente mendocino y actas seleccionadas de San Juan; se amplió la lectura del diario Santa Fe. No se tocaron atlas ni se imputaron residuos.

## Mendoza: 16 unidades, dos candidatos con cierre provincial

`mendoza_mesas_controles.csv` registra **188 posiciones de mesa** de la ciudad de Mendoza y 15 departamentos, con una posición sin cómputo localizado (San Martín 7). `mendoza_mesas_candidatos.csv` conserva las cifras por candidato, página PDF y fecha original/complementaria. `mendoza_totales_territoriales.csv` cuenta las mesas con/sin cifra para cada candidato.

La suma de cifras expresas da **Benegas 15.833 y Gaviola 8.247**, exactamente los totales del expediente 42-D-1912, PDF 105, página impresa 50. No se añadió ningún residuo para obtener ese cierre. Es un control provincial de los dos candidatos, no prueba de completitud de cada mesa ni de todas las fuerzas.

Los candidatos menores transcritos suman **70 frente a 74** en el resumen provincial, diferencia **-4**. No se repartieron esos cuatro votos. Las grafías de nombres se conservan y pueden duplicar personas (p. ej. José Antonio Delgado / José A. Delgado), por lo que no se certifica un conteo de personas únicas.

Las unidades de la fuente son: ciudad de Mendoza, San Rafael, Lavalle, Tupungato, Tunuyán, San Carlos, Rivadavia, Luján, Santa Rosa, La Paz, Junín, San Martín, Las Heras, Guaymallén, Godoy Cruz y Maipú. No se convirtió automáticamente ciudad de Mendoza en un polígono departamental actual, ni se desagregó San Rafael con límites posteriores.

### Resoluciones y complementarias

PDF 97-103 documenta anulación y repetición el **28 de abril**, escrutada el **30 de abril**, en San Carlos 1, San Martín 6/7/13/14, Guaymallén 5/7/8 y Maipú 11/13/14. Se conserva una fila por mesa con el cómputo último; no se sumó el escrutinio del 7/4 anulado. La mesa San Martín 7 está convocada pero no aparece con cómputo en la enumeración final consultada: queda vacía.

Ciudad de Mendoza 9/24/29/33 fueron primero aplazadas o anuladas, después reconsideradas y aprobadas en PDF 41, y escrutadas en PDF 43-45. Son mesas del 7/4, no complementarias. El registro retiene la última resolución.

### Reservas concretas

- Lavalle 9 no imprime cifra de Benegas; Maipú 14 no imprime cifra de Gaviola. Se conserva el vacío en el registro por mesa. Sus sumas territoriales se rotulan como sumas de cifras expresas, aunque el cómputo provincial coincida.
- Lavalle 8 asigna expresamente **todos los 102 votos de esa mesa a Gaviola**; Guaymallén 7/8 dice que todos los sobres estaban vacíos; San Martín 14 y Maipú 11 asignan todos los votos a Benegas. Sólo en esos casos exhaustivos se anotó cero para el otro candidato, con justificación en la nota. No proviene de calcular un residuo.
- Ciudad de Mendoza 6: los votos principales más el blanco exceden en uno los sobres; no se añadió una tarjeta por interpretación. Mesa 16 deja siete sobres sin distribución explícita; mesa 30 tiene diferencia de uno.
- Otras diferencias aritméticas están en `mendoza_cotejo_provincial.json`. **No todas son errores**: Tupungato 2 excluye ocho sobres, Tunuyán 4 excluye cuatro y Maipú 12 elimina votos de personas agregadas indebidamente al padrón (rango 126-151); eso explica diferencias de -8, -4 y -26. Permanecen anotadas, sin convertirlas en blancos.
- Santa Rosa 5, San Martín 12, Guaymallén 3/6 y Godoy Cruz 3 mantienen diferencias entre cifras expresas y sobres; no se armonizaron.

La tabla territorial principal incluye los candidatos menores efectivamente recuperados, con advertencia de exhaustividad pendiente. **No está certificada una tabla departamental de blancos, anulados o total de votantes**: cuando el acta no expresa una cifra, no se deriva para llenarla.

## San Juan: Angaco Sud/Norte y Calingasta

En la primera ampliación se registraron **9 mesas y 36 cifras por candidato**, desde PDF 63-66 y 76-77 del 27-D-1912. Los archivos actuales `san_juan_mesas_candidatos.csv` y `san_juan_mesas_controles.csv` contienen la ampliación posterior de 107 registros, descrita en PROGRESO_COMPETITIVAS_1912.md.

| Colegio/unidad literal | Mesas | Echegaray | Albarracín | Brandam | Garro |
|---|---:|---:|---:|---:|---:|
| Angaco Sud | 4 | 400 | 401 | 241 | 242 |
| Angaco Norte | 4 | 376 | 376 | 322 | 322 |
| Calingasta, complementaria | 1 | 123 | 121 | 79 | 84 |

Calingasta corresponde a la **complementaria del 21 de abril**, escrutada el 24; no se presenta como resultado original del 7/4 ni se suma a una mesa anulada. PDF 76 fija esa fecha y PDF 77 da los 205 sobres y las cuatro cifras.

Angaco Sud/Norte son nombres de colegios electorales tal como los escribe el acta; queda pendiente la correspondencia con geometría histórica. Hay varios candidatos por elector: no es válido comparar la suma de candidatos contra votantes como si fuese sufragio uninominal. Los controles ofrecen un diagnóstico condicional de dos votos por sufragante y de blancos por sobre; no certifican que todas las menciones manuscritas de blancos tengan igual significado. No se rellenan diferencias.

## Santa Fe: participación completa y una crónica del cierre

La edición del **16/4/1912**, p. 2, bajo “Junta Escrutadora Nacional”, publica el cuadro de inscripción/participación de los **19 departamentos**. `santa_fe_participacion_1912.csv` lo transcribe y `santa_fe_participacion_controles.json` conserva sumas y reservas. Es un control de cobertura, **no votos por candidato**.

- La suma de sufragantes departamentales es **74.878**, igual al total impreso. También cierran las **488 mesas**.
- Queda insegura una lectura de inscriptos de San Lorenzo; no se reconstruyó desde su participación ni del total.
- General Obligado imprime 5.838 inscriptos, 3.601 sufragantes y 2.257 no sufragantes: no cierra por veinte. El total de no sufragantes impreso es 23.493; las cifras transcritas suman 23.213. Se conserva la diferencia -280 sin corregir.
- Las Colonias tiene **28 mesas**, confirmado en la segunda lectura. No son 23.

La edición del **25/4**, p. 1, anuncia el resultado después de escrutar complementarias. `santa_fe_provincial_25abril.csv` contiene trece candidatos publicados. **Corrección del cotejo:** 36.747 corresponde a Araya en el diploma, no a Ávalos; no comparar candidatos distintos. `santa_fe_cotejo_diploma.csv` compara seis candidatos nominalmente. La crónica precede al cierre de la Junta del 26/4. Fernández aparece con **2.278**, por debajo de los **2.716** de la crónica del 23/4: contradicción pendiente, sin corrección automática.

La ampliación no añadió todavía departamentos santafesinos con votos por candidato: siguen cinco. Las páginas revisadas de 11/12/13 de abril y 25/27/28 de abril y 4 de mayo mezclan anuncios, opiniones, estadísticas y otros cargos; no se incorporó como voto departamental un dato que sólo era provincial o de participación. La primera sección de Rosario del 16/4 tampoco se sumó al total de Rosario del 18/4, para evitar duplicación.

## Próximo orden de trabajo

Orden histórico de la primera ampliación; quedó reemplazado por el de PROGRESO_COMPETITIVAS_1912.md y la decisión del usuario de relegar Tucumán y priorizar provincias competitivas.

1. Cotejar los cuatro votos menores faltantes de Mendoza y la posición San Martín 7 contra otra copia del acta o Diario de Sesiones. Las dos sumas principales ya cierran, pero no autorizan llenar vacíos.
2. Completar San Juan desde el mismo 27-D: ahora se conoce la separación entre escrutinio original, anulaciones y complementarias. Priorizar departamentos pequeños y mantener nombres históricos.
3. Obtener los otros departamentos de Santa Fe mediante las crónicas intermedias o las actas parciales del 17-D. Los cuadros de participación sirven para controlar cobertura, no para distribuir votos.
4. Tucumán continúa como fuente recuperada sin una nueva transcripción en esta ampliación: revisar 26-P preservando duplicados/correcciones como evidencia, sin contar dos veces una mesa.

Todos los localizadores y archivos nuevos se registran en `fuentes.csv` y en el log de teselas. Las imágenes derivadas sólo facilitan lectura; el original público y sus fechas se conservan.
