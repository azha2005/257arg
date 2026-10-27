# Brasil 2026: primera vuelta → balotaje

Estimaciones ecológicas a partir de los votos y padrones por sección del TSE, no observaciones de cambios individuales de voto.

[Abrir gráfico con selector de UF](sankey_brasil_2026p_2026b.html) | [PNG](sankey_brasil_2026p_2026b.png) | [Versión sin No votó](sankey_brasil_2026p_2026b_votantes.html) (misma estimación, sin la fila y la columna de abstención) | [Versión con No votó reducido](sankey_brasil_2026p_2026b_reducido.html) ([PNG](sankey_brasil_2026p_2026b_reducido.png); «No votó» dibujado a escala 1:4, cifras reales; [sin notas al pie](sankey_brasil_2026p_2026b_reducido_breve.html), [PNG](sankey_brasil_2026p_2026b_reducido_breve.png))

## Cobertura y fuentes

- 497.147 secciones, 94.021 locales y 5.712 municipios o localidades del exterior; 27 UF y exterior.
- 158.148.122 electores del balotaje: **99,62 %** del padrón publicado. No se extrapola el resto.
- ZIP completos del TSE en `datos_oficiales/brasil2026/`, con SHA256, metadatos HTTP y diccionarios transcritos. Las sumas de electores, comparecimiento, abstención, blancos, nulos y cada candidato cierran exactamente con los JSON nacionales del TSE ([cotejo](cotejo_totales_tse.json)).
- Particularidad: el CSV cuenta en QT_VOTOS_NOMINAIS los 5.246 votos del código 28 (Leonardo Araújo); el JSON los pasa a vnt. Se conserva la fila como opción observada.
- El catálogo advierte 39 registros duplicados por transferencias temporarias; no se restaron arbitrariamente.
- Regiones geográficas del IBGE (2017): 134 intermedias y 511 inmediatas, contando el exterior como una. Correspondencia de códigos TSE→IBGE y casos especiales en `brasil2026_regiones.py` ([tabla](regiones_municipio.csv)).

## Método

- Núcleo `rxc_calvo` del proyecto (mismo óptimo, calculado con estadísticos suficientes). Jerarquía: centro nacional → UF (penalización λ1 = 2e-06) → **región geográfica intermedia** (λ2 = 2e-05, hacia su UF).
- λ1, λ2 y el nivel se eligen por validación cruzada con municipios enteros por fold (5 folds; el centro y las UF se recalculan sin el fold). Regla del proyecto: la penalización más fuerte dentro del 1 % del mínimo, y el nivel más simple dentro del 1 % del mejor.
- Secciones comunes, instaladas, no anuladas, con cierre exacto entre votos y participación y padrón que cambia hasta 5 electores y 1 % (el origen se reescala al padrón de destino). Versión estricta con padrón idéntico como sensibilidad.
- Bootstrap: 200 réplicas de locales dentro de cada UF; en cada una se recalculan el centro nacional, λ1 y λ2 (grillas completas). Nivel y marginales de origen fijos.
- Sensibilidad por escala (local, municipio/zona, padrón idéntico): cada una elige su propia penalización y nivel por validación cruzada; con menos unidades, el ajuste de las secciones sobreajustaría.
- Además del intervalo bootstrap, `intervalos.csv` trae el **rango entre especificaciones** (UF sola, el otro nivel regional, local, municipio/zona, padrón idéntico y Calvo): es la incertidumbre de modelo que el bootstrap no ve.

### Validación cruzada (error por sección, puntos, sin No votó)

| Nivel | Error con su λ |
|---|---:|
| UF | 1,784 |
| región geográfica intermedia | 1,756 |
| región geográfica inmediata | 1,767 |

### Fuera de muestra: predecir municipios que no entraron al ajuste

3 repeticiones × 5 folds de municipios enteros; error ponderado por electores del balotaje, como en [fuera_de_muestra](../fuera_de_muestra/RESUMEN.md). «sin origen» = reparto medio de la UF; «media nacional» = reparto medio del país. Por UF en [fuera_de_muestra.csv](fuera_de_muestra.csv).

| Modelo | Todas las categorías | Solo votantes |
|---|---:|---:|
| media nacional | 10,190 | 13,413 |
| sin origen | 7,416 | 9,713 |
| Calvo (nacional) | 2,143 | 1,967 |
| centro nacional | 2,142 | 1,970 |
| UF | 1,956 | 1,844 |
| intermedia | 1,925 | 1,824 |
| inmediata | 1,939 | 1,832 |

La matriz por región geográfica intermedia reduce el error fuera de muestra 1,6 % respecto de la de UF. Buena parte del error es ruido de cada sección (unos 300 electores), que ningún modelo puede bajar; la mejora sobre la parte sistemática es mayor que ese porcentaje.

## Matriz principal: porcentaje de cada origen

| Origen | Lula (PT) | Flávio Bolsonaro (PL) | Blanco y nulo | No votó | Auditoría |
|---|---:|---:|---:|---:|---|
| Flávio Bolsonaro (PL) | 0,0 % | 99,8 % | 0,0 % | 0,2 % | borde: Lula (PT), Blanco y nulo, No votó |
| Lula (PT) | 100,0 % | 0,0 % | 0,0 % | 0,0 % | borde: Flávio Bolsonaro (PL), Blanco y nulo, No votó |
| Augusto Cury | 52,7 % | 25,5 % | 18,5 % | 3,3 % | Sensible |
| Renan Santos | 41,8 % | 37,5 % | 19,8 % | 1,0 % | Sensible |
| Ronaldo Caiado | 35,8 % | 52,0 % | 10,6 % | 1,6 % | Sin alerta por estos criterios |
| Romeu Zema | 0,1 % | 99,6 % | 0,1 % | 0,2 % | borde: Lula (PT), Blanco y nulo, No votó |
| Samara Martins | 90,6 % | 2,4 % | 4,5 % | 2,4 % | Sensible |
| Hertz Dias | 94,6 % | 1,4 % | 1,4 % | 2,6 % | No identificada |
| Clariana Barão | 28,1 % | 15,3 % | 25,1 % | 31,5 % | Sensible |
| Edmilson Costa | 51,8 % | 10,8 % | 23,3 % | 14,0 % | No identificada |
| Wilson Grassi | 33,5 % | 31,7 % | 20,6 % | 14,2 % | No identificada |
| Rui Costa Pimenta | 35,8 % | 38,8 % | 13,5 % | 11,9 % | No identificada |
| Leonardo Araújo | 30,7 % | 18,7 % | 25,7 % | 24,9 % | Sensible |
| Blanco y nulo | 61,8 % | 0,0 % | 38,2 % | 0,1 % | borde: Flávio Bolsonaro (PL), No votó |
| No votó | 8,2 % | 1,3 % | 1,4 % | 89,0 % | Sin alerta por estos criterios |

### Qué tan seguro es cada reparto hacia los finalistas

Bootstrap 5–95 y rango entre especificaciones, en % de la fila.

| Origen | → Lula | IC | Modelos | → Flávio | IC | Modelos |
|---|---:|---|---|---:|---|---|
| Flávio Bolsonaro (PL) | 0,0 % | 0,0 % – 0,1 % | 0,0 % – 0,2 % | 99,8 % | 99,1 % – 99,8 % | 99,1 % – 100,0 % |
| Lula (PT) | 100,0 % | 99,8 % – 100,0 % | 98,8 % – 100,0 % | 0,0 % | 0,0 % – 0,0 % | 0,0 % – 0,0 % |
| Augusto Cury | 52,7 % | 51,8 % – 53,4 % | 52,0 % – 55,7 % | 25,5 % | 24,7 % – 27,4 % | 11,2 % – 27,8 % |
| Renan Santos | 41,8 % | 41,6 % – 42,8 % | 36,2 % – 50,3 % | 37,5 % | 36,7 % – 38,1 % | 35,7 % – 45,6 % |
| Ronaldo Caiado | 35,8 % | 34,4 % – 36,4 % | 26,3 % – 35,9 % | 52,0 % | 51,5 % – 52,7 % | 51,4 % – 60,4 % |
| Romeu Zema | 0,1 % | 0,1 % – 0,9 % | 0,1 % – 2,5 % | 99,6 % | 98,7 % – 99,6 % | 91,5 % – 99,6 % |
| Samara Martins | 90,6 % | 87,6 % – 92,7 % | 72,9 % – 94,9 % | 2,4 % | 1,5 % – 4,7 % | 1,3 % – 9,2 % |
| Hertz Dias | 94,6 % | 93,6 % – 96,2 % | 50,6 % – 95,3 % | 1,4 % | 0,9 % – 1,9 % | 1,3 % – 15,5 % |
| Clariana Barão | 28,1 % | 19,2 % – 38,9 % | 15,8 % – 36,0 % | 15,3 % | 10,1 % – 21,2 % | 11,5 % – 22,3 % |
| Edmilson Costa | 51,8 % | 41,9 % – 59,7 % | 16,7 % – 56,4 % | 10,8 % | 6,6 % – 17,5 % | 8,4 % – 22,8 % |
| Wilson Grassi | 33,5 % | 24,4 % – 42,1 % | 12,5 % – 36,3 % | 31,7 % | 24,1 % – 39,9 % | 24,6 % – 49,0 % |
| Rui Costa Pimenta | 35,8 % | 28,5 % – 43,9 % | 15,7 % – 37,7 % | 38,8 % | 30,3 % – 47,1 % | 23,8 % – 59,0 % |
| Leonardo Araújo | 30,7 % | 18,6 % – 43,6 % | 19,9 % – 36,5 % | 18,7 % | 11,4 % – 28,9 % | 14,8 % – 25,2 % |
| Blanco y nulo | 61,8 % | 61,7 % – 62,4 % | 61,4 % – 68,8 % | 0,0 % | 0,0 % – 0,0 % | 0,0 % – 0,3 % |
| No votó | 8,2 % | 8,0 % – 8,3 % | 7,0 % – 8,4 % | 1,3 % | 1,1 % – 2,0 % | 0,2 % – 2,7 % |

## Auditoría

- **No identificada**: diferencia principal/Calvo >30 puntos (o >20 si la fila pesa menos de 5 % del padrón), o >20 entre escalas o especificaciones. **Sensible**: alguna de esas diferencias >10 puntos. Detalle en [AUDITORIA.md](../AUDITORIA.md) y [auditoria_filas.csv](auditoria_filas.csv).
- **Celdas en el borde** (<0,5 % de la fila): 11. El modelo no puede dar menos de 0, así que una celda en 0,0 % quiere decir «pocos, sin poder decir cuántos», no «nadie». En el sankey llevan ‡ en la fila y una nota al pasar el cursor.

  - Flávio Bolsonaro (PL) → Lula (PT): 0,00 % (p95 0,10 %)
  - Flávio Bolsonaro (PL) → Blanco y nulo: 0,01 % (p95 0,14 %)
  - Flávio Bolsonaro (PL) → No votó: 0,18 % (p95 0,64 %)
  - Lula (PT) → Flávio Bolsonaro (PL): 0,00 % (p95 0,00 %)
  - Lula (PT) → Blanco y nulo: 0,00 % (p95 0,04 %)
  - Lula (PT) → No votó: 0,00 % (p95 0,12 %)
  - Blanco y nulo → Flávio Bolsonaro (PL): 0,01 % (p95 0,01 %)
  - Blanco y nulo → No votó: 0,06 % (p95 0,07 %)
  - Las filas de menos de 1 % del padrón con celdas en el borde están en el CSV.

- Error territorial ponderado con la matriz de cada región: 1,871 puntos.
- Entre la principal y Calvo se redistribuyen 1.757.126 votos (1,11 % de la masa modelada).
- Destinos por UF con más del 125 % de sus votos reales + 2.000: 0.

| Variante | Unidades | Electores | Mayor cambio en una celda |
|---|---:|---:|---:|
| UF | 497.147 | 158.148.122 | 0,66 puntos |
| inmediata | 497.147 | 158.148.122 | 0,70 puntos |
| local | 94.021 | 158.148.122 | 35,10 puntos |
| munzona | 6.247 | 158.148.122 | 43,99 puntos |
| estricta | 443.483 | 140.121.114 | 7,93 puntos |

Las mayores diferencias recaen en filas pequeñas. La versión estricta cambia la muestra.

## Destinos: observados frente a estimados en las secciones usadas

| Destino | Observado | Estimado | Diferencia |
|---|---:|---:|---:|
| Lula (PT) | 64.011.000 | 64.134.019 | 123.019 |
| Flávio Bolsonaro (PL) | 59.589.054 | 59.781.983 | 192.929 |
| Blanco y nulo | 4.139.976 | 4.215.735 | 75.759 |
| No votó | 30.408.092 | 30.016.385 | -391.707 |

## Archivos y reproducción

[Matriz porcentual](matriz_pct.csv), [votos estimados](matriz_votos.csv), [intervalos y rango de modelos](intervalos.csv), [variante Calvo](calvo_nacional.csv), [matriz por UF](por_provincia.csv), [matriz por región](por_region.csv), [control completo](control.json), [controles marginales](control_marginales_uf.csv), [cobertura](cobertura_por_uf.csv), [exclusiones](exclusiones.csv), [fallos de calidad](fallos_calidad.csv), [códigos de candidatos](candidatos_codigos.csv); matrices de sensibilidad `matriz_votos_{local,munzona,estricta}.csv`.

Desde la raíz:

```
python -X utf8 transferencias/brasil2026_datos.py
python -X utf8 transferencias/brasil2026_datos.py --preparar
python -X utf8 transferencias/brasil2026_datos.py --cotejar
python -X utf8 transferencias/brasil2026_estimar.py --preparar
python -X utf8 transferencias/brasil2026_regiones.py
python -X utf8 transferencias/brasil2026_estimar.py
python -X utf8 transferencias/brasil2026_presentar.py
python -X utf8 transferencias/brasil2026_revisar_html.py
python -X utf8 transferencias/brasil2026_verificar.py
python -X utf8 transferencias/auditar.py
```

WORKERS=4 y BOOT=200 por defecto, con prioridad baja; la corrida completa tardó 56 minutos. Un ZIP local solo se reutiliza si coincide su SHA256 guardado. Para una actualización, no reutilizar `pareadas.pkl` de una versión anterior.
