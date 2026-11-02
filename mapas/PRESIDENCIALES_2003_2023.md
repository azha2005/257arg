# Serie presidencial nacional, 2003–2023

Ocho atlas por departamento, partido y circunscripción/comuna de Capital; los siete recuadros y la leyenda del constructor vigente de diputados. No son estimaciones por radio.

| Año | Primera vuelta | Segunda vuelta | Diputados del mismo año |
|---|---|---|---|
| 2003 | [Atlas](mapa2003pres/atlas_2003pres.html) | No se celebró | [Atlas](mapa2003/atlas_2003.html) |
| 2007 | [Atlas](mapa2007pres/atlas_2007pres.html) | No hubo | [Atlas](mapa2007/atlas_2007.html) |
| 2011 | [Atlas](mapa2011pres/atlas_2011pres.html) | No hubo | [Atlas](mapa2011/atlas_2011.html) |
| 2015 | [Atlas](mapa2015pres/atlas_2015pres.html) | [Balotaje](mapa2015bal/atlas_2015bal.html) | [Atlas](mapa2015/atlas_2015.html) |
| 2019 | [Atlas](mapa2019pres/atlas_2019pres.html) | No hubo | [Atlas](mapa2019/atlas_2019.html) |
| 2023 | [Atlas](mapa2023pres/atlas_2023pres.html) | [Balotaje](mapa2023bal/atlas_2023bal.html) | [Atlas](mapa2023/atlas_2023.html) |

Los doce atlas de diputados 2003–2025 ya existentes siguen incluidos en `sitio/catalogo.py`; se agregó una sección presidencial aparte. Los HTML nuevos enlazan diputados del año y la otra vuelta cuando corresponde. No se incorpora el ensayo 2007 por circuito que el usuario excluyó del sitio.

## Datos y límites

- Mapa: PolAr/Andy Tow para 2003–2007 y DINE, provisorio por mesa, para 2011–2023, agregados por departamento sin recalibrar votos. Torta, barras y métricas nacionales: tablas de Wikipedia ya conservadas en el proyecto. Cada atlas tiene comparación por candidatura y SHA256 de sus insumos.
- Logos: recursos existentes de los atlas por radio. **Imágenes, posición, marco y zoom se copian de la versión por radio de cada elección**, sin ampliación adicional en el nacional (corrección pedida por el usuario). En 2003 se conservan exactamente los cinco logos y su tratamiento propio del AMBA 2003 por radio. Los atlas por radio de origen no se modifican.
- Complementos: fuentes locales documentadas en `datos/fuentes_leg2003_2025/presidenciales/complementos.json`; se comprueba que cada tabla cierre. Las doce consultas por sección completa de los balotajes se descargaron de la CNE con autorización expresa del usuario; archivos y filtros en `datos/fuentes_leg2003_2025/presidenciales/busqueda_faltantes/cne/`. Los inscriptos fueron transcritos de la pantalla, ya que no figuran en los XLS exportados.
- Participación local: sobre electores de mesas con votos que trae el agregado. Los complementos definitivos tienen su propio padrón cuando está publicado. No se infieren inscriptos ausentes ni se muestra participación si los votantes superan ese padrón.
- 2007: **Sarmiento, Santiago del Estero, resuelto con el escrutinio definitivo DINE**, página 31 de `Sgo_Estero_28_Oct_07.pdf` recuperado de Wayback. FPV 1299, PO 2; 1424 positivos, 1467 votantes y 2615 electores. Se reemplaza íntegramente la tabla dudosa de PolAr, sin imputar ni restar votos. El atlas 2007 queda con cobertura departamental completa.
- Balotaje 2015: Antofagasta de la Sierra, Valle Grande, Rivadavia (Salta) y Santa Victoria completados con las consultas definitivas de la CNE del 22/11/2015. Los cuatro gana Scioli.
- Balotaje 2023: Antofagasta de la Sierra, Florentino Ameghino (Chubut), Gastre, Telsen, Susques, Valle Grande, Curacó y Santa Victoria completados con las consultas definitivas de la CNE del 19/11/2023. Milei gana Antofagasta, Florentino Ameghino, Telsen y Susques; Massa gana Gastre, Valle Grande, Curacó y Santa Victoria.
- **Los ocho atlas nacionales tienen cobertura departamental completa**. Malvinas permanece gris; Antártida lleva resultado separado. La geometría censal y los acercamientos siguen las aproximaciones documentadas del proyecto.

## Construcción y revisión

`python mapas/mapa2003pres/build_2003pres.py` (análogos en las otras siete carpetas).

`python herramientas/validar_pres2003_2023.py --render` comprueba datos, candidatos ganadores, logos 2003, todas las pestañas, título, leyendas, errores JS y los doce atlas de diputados del catálogo. Genera PNG blancos y transparentes con el verificador vigente del proyecto.

`python sitio/armar.py miniaturas mapa2003pres` (análogos para las otras siete claves), `python sitio/armar.py indice` y `python sitio/armar.py copiar <destino>` preparan el sitio local. El despliegue remoto depende del push y de GitHub Actions. Sin paquetes de Commons.
