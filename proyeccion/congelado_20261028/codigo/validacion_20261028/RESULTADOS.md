# Correcciones implementadas y medición de la proyección argentina

28 de octubre de 2026. Código anterior conservado en `baseline/`. No se cambiaron las transcripciones ni se incorporaron votos inventados.

## Resultado principal

La corrección mejora modestamente los porcentajes nacionales y evita errores de identidad, datos ausentes y probabilidades. No se encontró una mejora uniforme en bancas. Se conservan Goodman λ=0,1 y factor 1,4 para fotos; no se retocaron para acertar las 27 actas reales.

## Qué se corrigió

- El backtest mantiene todo voto disponible de destino, con respaldo histórico por circuito, sección o distrito. Las filas sin resultados finales se distinguen de abstenciones; no se imputa su voto.
- El repesado AMBA/resto se calcula sobre las actas que informan cada fuerza y se repite en cada remuestra.
- Identidad electoral independiente del nombre de la foto; se colapsan copias iguales y se rechazan versiones contradictorias.
- Catálogo de fuerzas separado de las fotos; cero observado, desconocido y lista no presentada son estados distintos. Sin soporte, bandas y probabilidades quedan no estimables.
- Primer puesto se compara contra todas las fuerzas, no solo contra el segundo de la estimación puntual.
- Porcentajes nacionales y bancas salen de los mismos votos distritales y remuestras. Las actas parciales no reducen el prior de una fuerza no informada. La actualización provincial remuestrea las actas y su covarianza con el modelo.
- Se usa padrón de destino y se prohíben votos a listas ausentes de cada distrito. Las tablas agregadas OTRAS no se interpretan como fotos con detalle de listas provinciales.
- La aguja masiva usa D sin benchmarking y remuestrea el estimador completo, manteniendo fijos los votos ya conocidos. El prior del ICG usa solo años anteriores por defecto y sigue desactivado en la proyección de fotos.

## Diseño de la medición

1.000 colecciones de exactamente 30 mesas por versión: 100 por combinación de elección destino y esquema. Destinos: balotajes 2015 y 2023, general 2023 y diputados 2025. Para las generales se promedian dos orígenes, como el programa operativo. Son cuatro elecciones destino, no 1.000 elecciones independientes.

Azar: 30 mesas uniformes. Tipo Twitter: 20 del AMBA y 10 del resto, con racimos AMBA de hasta 10+3+3 mesas y completando siempre a 30 únicas. Twitter parcial: mismo diseño, ocultando a terceros en las primeras diez actas; se mantienen los dos principales del destino como escenario sintético. No reproduce todos los mecanismos reales de publicación de fotos.

Ambas versiones reciben las mismas 30 mesas y se comparan contra todo el provisorio disponible. La anterior descarta actas sin cruce histórico y retiene entre 28 y 30; la corregida conserva las 30 en las 1.000 corridas. La columna actas de los CSV cuenta las retenidas, no las entregadas. La nueva usa el marco de electores de destino y respaldo de origen; la anterior mantiene su comportamiento original. Los electores por mesa de las fotos no se entregan al modelo: los estima como en operación. Cada corrida usa 200 remuestras de circuitos. El factor de banda 1,4 estaba fijado antes de estas pruebas. Las semillas son nuevas, pero las elecciones ya se habían usado en el desarrollo: esto es evaluación retrospectiva emparejada, no validación prospectiva.

## Error del margen y cobertura

Errores en puntos porcentuales. Cobertura de banda nominal 95 %, medida para el margen entre los dos primeros reales. Con 100 colecciones, diferencias de pocos puntos de cobertura tienen incertidumbre de Monte Carlo apreciable.

| Destino | Muestra | Error antes | Error después | Cobertura antes | Cobertura después |
|---|---|---:|---:|---:|---:|
| 2025bl | 30 al azar | 2.023 | 1.913 | 96 % | 96 % |
| 2025bl | 30 tipo Twitter | 2.895 | 2.868 | 92 % | 93 % |
| 2025bl | 30 Twitter, 10 parciales | 3.111 | 3.117 | 95 % | 95 % |
| 2023p | 30 al azar | 1.926 | 1.963 | 98 % | 98 % |
| 2023p | 30 tipo Twitter | 2.276 | 2.307 | 99 % | 99 % |
| 2023p | 30 Twitter, 10 parciales | 2.315 | 2.317 | 99 % | 99 % |
| 2023b | 30 al azar | 1.569 | 1.563 | 96 % | 97 % |
| 2023b | 30 tipo Twitter | 2.114 | 2.127 | 97 % | 97 % |
| 2015b | 30 al azar | 1.736 | 1.695 | 94 % | 94 % |
| 2015b | 30 tipo Twitter | 2.452 | 2.448 | 98 % | 97 % |

La ganancia del margen no es uniforme: en general 2023 sube unas centésimas y en otros pares baja. `resumen_fotos.csv` incluye diferencias emparejadas e intervalos Monte Carlo; estos cuantifican las colecciones simuladas y no la incertidumbre sobre futuras elecciones.

## Error por fuerza

| Destino | Muestra | Media antes | Media después |
|---|---|---:|---:|
| 2025bl | 30 al azar | 1.110 | 1.085 |
| 2025bl | 30 tipo Twitter | 1.658 | 1.638 |
| 2025bl | 30 Twitter, 10 parciales | 1.702 | 1.612 |
| 2023p | 30 al azar | 0.910 | 0.900 |
| 2023p | 30 tipo Twitter | 1.105 | 1.095 |
| 2023p | 30 Twitter, 10 parciales | 1.138 | 1.042 |
| 2023b | 30 al azar | 0.784 | 0.782 |
| 2023b | 30 tipo Twitter | 1.057 | 1.064 |
| 2015b | 30 al azar | 0.868 | 0.847 |
| 2015b | 30 tipo Twitter | 1.226 | 1.224 |

Con fotos parciales, la reducción del error medio por fuerza es 8,5 % en 2023 y 5,3 % en 2025. Esto no implica una reducción equivalente del margen.

## Bancas: 50 colecciones por esquema

Se midieron 150 colecciones por versión, 100 remuestras cada una, con las primeras 50 muestras de cada esquema de 2025. La referencia real son las bancas calculadas a partir de listas y padrón locales: LLA 64, FP 47, PU 8, FIT 3, otras 5. Ambos modelos conservan el prior provincial y el supuesto Zipf; la nueva versión corrige su aplicación y hace coherente el nacional.

| Muestra | Fuerza | Error absoluto antes | Error absoluto después | Cobertura 90 % antes | Después |
|---|---|---:|---:|---:|---:|
| 30 al azar | FIT | 0.98 | 0.94 | 92 % | 96 % |
| 30 al azar | FP | 1.28 | 1.32 | 100 % | 100 % |
| 30 al azar | LLA | 2.90 | 2.84 | 92 % | 90 % |
| 30 al azar | PROV | 2.38 | 2.44 | 96 % | 96 % |
| 30 al azar | PU | 1.58 | 1.58 | 98 % | 100 % |
| 30 tipo Twitter | FIT | 0.98 | 0.96 | 88 % | 88 % |
| 30 tipo Twitter | FP | 2.24 | 2.44 | 92 % | 94 % |
| 30 tipo Twitter | LLA | 3.24 | 3.46 | 94 % | 94 % |
| 30 tipo Twitter | PROV | 2.84 | 2.94 | 94 % | 94 % |
| 30 tipo Twitter | PU | 1.86 | 1.76 | 100 % | 100 % |
| 30 Twitter, 10 parciales | FIT | 1.24 | 0.94 | 88 % | 92 % |
| 30 Twitter, 10 parciales | FP | 2.40 | 2.38 | 98 % | 98 % |
| 30 Twitter, 10 parciales | LLA | 3.64 | 3.62 | 94 % | 90 % |
| 30 Twitter, 10 parciales | PROV | 3.12 | 3.06 | 96 % | 94 % |
| 30 Twitter, 10 parciales | PU | 1.92 | 1.84 | 100 % | 100 % |

No hubo mejora uniforme: persiste la subestimación de LLA y la sobreestimación de fuerzas menores en parte de las simulaciones. No se ajustó el perfil Zipf ni la retención de gobernadores con estos errores de 2025. La corrección del procedimiento sigue siendo necesaria, aunque empeore alguna métrica: evita aparentes aciertos producidos por errores que se compensan.

## Las actas reales de Twitter

Son 27 mesas únicas en 16 circuitos, 20 del AMBA y 11 actas incompletas. Se usaron las transcripciones originales, sin seleccionar una submuestra favorable. Punto nacional: 2.000 remuestras; Congreso: 300 de las mismas remuestras.

| Fuerza | Antes, sin corrección provincial nacional | Corregido, sin prior provincial | Corregido, coherente con Congreso | Real |
|---|---:|---:|---:|---:|
| LLA | 43.03 | 42.93 | 41.55 | 40.66 |
| FP | 35.78 | 35.92 | 34.30 | 33.60 |
| PU | 5.28 | 5.29 | 7.93 | 7.68 |
| FIT | 4.87 | 4.83 | 4.67 | 3.90 |
| OTRAS | 11.03 | 11.03 | 11.55 | 14.16 |

Margen LLA−FP: antes **+7.251**, corregido sin prior provincial **+7.004**, conjunto votos+bancas **+7.252**; real **+7.054**.

Bancas corregidas: **LLA 62, FP 49, PU 8, FIT 3, otras 5**. El punto no cambió respecto de la versión previa con gobernadores: dos bancas transferidas de LLA a FP respecto de la referencia real. Las bandas ahora provienen de las mismas remuestras que los porcentajes nacionales.

El buen margen de estas 27 mesas no vuelve exacto el detalle: OTRAS sigue subestimado aproximadamente 2,6 puntos en el modelo con Congreso.

## Escrutinio masivo y cobertura fuera de la calibración

Seis repeticiones por tipo de llegada (cinco tipos), cinco cortes (0,2 %, 1 %, 5 %, 25 %, 50 %) y tres métodos: 1.350 evaluaciones. Todos incluyen los 24 distritos y el 100 % de votos disponibles en los archivos de destino. No significa 100 % de votos definitivos: las mesas sin resultados en el provisorio siguen siendo desconocidas.

| Par | D con benchmarking | D sin ajuste | E sin ajuste |
|---|---:|---:|---:|
| 2015p->2015b | 0.697 | 0.513 | 0.436 |
| 2019p->2023p | 1.337 | 1.066 | 0.970 |
| 2023p->2023b | 0.400 | 0.369 | 0.348 |

Se implementó D sin ajuste como base de la aguja. E queda como variante experimental: su ventaja todavía debe contrastarse en otros destinos. El benchmarking podía introducir votos negativos después del recorte; en esta prueba D llegó a -9.10 votos en una celda. D y E sin ajuste conservaron no negatividad.

Para el error sistemático entre años se añadió un piso de desviación `1,8 × (1−fracción)`, calibrado exclusivamente con 2019→2023 donde la fórmula anterior quedaba corta. Se evaluó sin retocarlo con 2023→2025: 3 trayectorias por cada uno de 5 órdenes, 4 cortes, 60 remuestras por corte. Es una prueba pequeña y los cortes de una trayectoria son dependientes.

| Orden | Cobertura LLA | FP | PU | FIT | OTRAS |
|---|---:|---:|---:|---:|---:|
| azar | 100.0 % | 100.0 % | 100.0 % | 100.0 % | 100.0 % |
| capital | 100.0 % | 100.0 % | 100.0 % | 100.0 % | 100.0 % |
| geo | 100.0 % | 100.0 % | 100.0 % | 100.0 % | 100.0 % |
| geo_circ | 100.0 % | 100.0 % | 100.0 % | 100.0 % | 91.7 % |
| sesgo | 66.7 % | 83.3 % | 100.0 % | 100.0 % | 41.7 % |

**Limitación abierta:** en el estrés donde entran primero las secciones favorables al ganador, la cobertura de LLA queda en 66,7 % y la de OTRAS en 41,7 %. No se presenta esta banda como calibrada al 95 % para cualquier selección. La página muestra bandas nominales y frecuencias de simulación con esta reserva. No se amplió a posteriori usando 2025 para aparentar que pasó la prueba.

## Pruebas y reproducción

11 pruebas de regresión pasan: duplicados y conflictos, pesos por fuerza, catálogo y datos ausentes, probabilidad conjunta, prior provincial con actas parciales, respaldo histórico, identidad de votos/bancas, equivalencia numérica de la ruta optimizada y conservación de todos los votos observados.

```powershell
python -X utf8 proyeccion/validacion_20261028/medir.py --version antes --reps 100 --boot 200
python -X utf8 proyeccion/validacion_20261028/medir.py --version despues --reps 100 --boot 200
python -X utf8 proyeccion/validacion_20261028/medir.py --version antes --reps 50 --boot 100 --destinos 2025bl --bancas
python -X utf8 proyeccion/validacion_20261028/medir.py --version despues --reps 50 --boot 100 --destinos 2025bl --bancas
python -X utf8 proyeccion/validacion_20261028/escrutinio.py
python -X utf8 proyeccion/validacion_20261028/cobertura_aguja.py
python -X utf8 proyeccion/validacion_20261028/reales.py antes
python -X utf8 proyeccion/validacion_20261028/reales.py despues
python -W ignore::DeprecationWarning -W ignore::ResourceWarning -X utf8 proyeccion/test_correcciones.py
python -X utf8 proyeccion/proyectar_fotos.py proyeccion/fotos25/actas.csv --origen 2023p,2021bl --real 2025bl --congreso 2025
python -X utf8 proyeccion/aguja_fotos.py
python -X utf8 proyeccion/validacion_20261028/informe.py
```

Para una elección futura: proporcionar `--marco` con distrito_id, seccion_id, circuito, e, más el catálogo de fuerzas y los antecesores revisados. Las fotos pueden incluir `electores`; si falta se estima desde el origen. Para Congreso son obligatorios el padrón y el catálogo de listas del año; no se reutiliza silenciosamente el padrón de una elección anterior.

## Archivos

- `fotos_antes/despues.csv` y `_fuerzas.csv`: resultados por muestra y por fuerza.
- `bancas_antes/despues_escanos.csv`: comparación de las bancas por muestra.
- `resumen_fotos.csv`, `resumen_bancas.csv`: tablas agregadas.
- `twitter_real_antes/despues.json`: las 27 actas reales.
- `universos_completos.json`, `escrutinio_completo.csv`, `aguja_cobertura_2025.csv`: universo, modelos y prueba de bandas.
- `baseline/`: copia previa de los modelos y de los informes/gráfico reales; los otros informes históricos fuera de esta carpeta conservan su fecha y método anterior.
- `../fotos25/actas_proyeccion.md`, `../fotos25/actas_congreso.html`, `../img/aguja_fotos_2025.png`: salidas operativas actualizadas.

![Comparación de 30 mesas](comparacion_30_mesas.png)
