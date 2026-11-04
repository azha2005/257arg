# Artículos: previsualizaciones pendientes de revisión

30-oct-2026. Se prepararon 17 artículos para incorporar los 20 atlas autorizados de generales y PASO de 2003–2025. **No se publicó ninguna edición.** El usuario pidió ver las previsualizaciones antes de enviar; se requiere su visto bueno antes de pulsar «Publicar cambios».

- Doce generales: 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023 y 2025.
- Cinco artículos de PASO: 2011, 2017, 2019, 2021 y 2023. En 2011, 2019 y 2023 se incluyen presidenciales y diputados por separado.
- Se conservan todos los mapas anteriores; el nuevo es la primera opción de Switcher. En 2021 se conservan sus dos opciones anteriores. 2003 y 2005 no tenían mapa previo y se agrega directamente.
- Cada atlas tiene sección de resultados por departamento y galería de coropletas, con participación disponible. Se explicitan La Pampa 2003 y las unidades sin mesas en 2013.
- Se mantienen en espera 2013paso, 2015paso y 2015pasodip.

Las pestañas de Chrome quedaron con previsualizaciones reales de Wikipedia (action=submit por previsualización, no por publicación), marcadas para revisión. No recargar estas páginas: perderían el POST de la vista previa.

Orden e identificadores de pestañas: 00=897021495, 01=897021501, 02=897021504, 03=897021507, 04=897021513, 05=897021516, 06=897021519, 07=897021522, 08=897021525, 09=897021528, 10=897021531, 11=897021534, 12=897021537, 13=897021540, 14=897021543, 15=897021546, 16=897021549.

Archivos: `plan.json`; `NN.json` y `NN_original.wiki` con revisiones de origen; `NN_propuesto.wiki`; `NN.diff`; `editar_NN.html` para recuperar el contenido. El servidor local en 127.0.0.1:8766 sirve solo esta carpeta durante la revisión.

Antes de publicar tras la aprobación: comprobar que las revisiones de origen sigan vigentes o integrar los cambios concurrentes; verificar vistas y botones; publicar mediante Chrome y auditar las revisiones resultantes. No volver a ejecutar la descarga sobre estos originales sin conservar las propuestas revisadas.

## Autorizacion y bloqueo posterior
El usuario aprobo publicar todos los cambios. Auditoria en previo_publicacion.json: 2003, 2005, 2007 y 2009 ya estaban publicados con el texto propuesto (2009 desde cuenta temporal). Los otros 13 conservan el original. Al intentar publicar 2011 como ItsAHardLife, Wikipedia solicito hCaptcha y no guardo la edicion. Pestana de entrega 897021569: texto propuesto completo y resumen cargados. Esperar que el usuario complete el CAPTCHA; no resolverlo sin autorizacion especifica. No volver a pedir aprobacion del contenido, que ya esta concedida.

## Reapertura tras cerrar Chrome
Auditoria revision_reapertura.json: 2003, 2005, 2007 y 2009 publicados; otros 13 pendientes al iniciar esta reapertura. Se recrearon las 13 previsualizaciones y se verifico que no muestran el error de perdida de sesion. PASO 2023 verificada mediante arbol visible tras fallos transitorios de Chrome. El usuario publicara manualmente y resolvera CAPTCHA si aparece. No se pulso Publicar cambios durante la reapertura. Se observo que 2013 ya paso a vista de articulo mientras el usuario revisaba; requiere auditoria posterior para confirmar su publicacion.
Pestanas nuevas: 2011=897021955, 2013=897021958, 2015=897021961, 2017=897021964, 2019=897021967, 2021=897021970, 2023=897021973, 2025=897021990; PASO 2011=897021993, 2017=897021996, 2019=897021999, 2021=897022002, 2023=897022005.

## Publicacion final confirmada
El usuario publico todas las vistas. Auditoria de lectura de la API: los 17 articulos coinciden exactamente (salvo espacios externos) con las propuestas aprobadas. Revisiones, usuarios y fechas en auditoria_final.json. No quedan articulos pendientes de esta tanda.

## Presidenciales 1995 y 1999
24 archivos publicados y cotejados SHA1: todos IGUAL, detalle en pres_auditoria.json. Reemplazo del mapa departamental antiguo por el nuevo con leyenda, mapa provincial de ficha conservado, galeria del voto por formula agregada. Originales, propuestas y diffs pres_1995 y pres_1999 guardados. Ambas previsualizaciones reales verificadas sin perdida de sesion; pestanas 897022050 y 897022053 marcadas para entrega. No se publicaron las ediciones de Wikipedia: quedan para revision y envio manual del usuario.

## Correccion solicitada: retirar mapas antiguos
Por instruccion expresa del usuario se eliminaron de ambas propuestas los mapas antiguos de la ficha y de resultados, y el selector de versiones. Solo quedan los mapas propios. Propuestas y diffs actualizados; pendiente cargar previsualizaciones cuando se habilite el navegador.
