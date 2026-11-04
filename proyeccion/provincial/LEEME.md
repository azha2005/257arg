# Proyección de elecciones provinciales con pocas mesas (29-oct-2026)

El motor nacional (`proyeccion/fotos_motor.py`, el congelado el 28-oct con un solo agregado: el parámetro opcional
`estrato`, que por defecto deja todo igual) aplicado a una provincia. Cambia tres cosas:

1. Solo las mesas de la provincia, de las actas y de los orígenes.
2. La unidad de informe ocupa el lugar del distrito: en la PBA, las 8 secciones electorales
   (`seccionprovincial_id` de `datos_oficiales/2025/x/ambitosElectorales.csv`; también vienen para Mendoza y Tucumán).
   La regresión es una sola para toda la provincia; el resultado se suma por sección.
3. Las actas se repesan por los estratos de la provincia: en la PBA, los 24 partidos del conurbano contra el interior.

Con la proyección por sección se reparten las bancas con la regla de la provincia (PBA: cociente Hare por sección,
solo las listas que lo alcanzan entran a los restos; Ley 5109, arts. 109-110). OTRAS cuenta para el cociente pero
no recibe bancas.

## Archivos

| Archivo | Qué hace |
|---|---|
| `config.py` | provincias (distrito, unidad, estratos, cámaras, renovación) y elecciones provinciales por mesa |
| `ingestar.py <clave>` | CSV provincial por mesa → `proyeccion/mesas_<clave>.pkl` y `circ_<clave>.pkl` (formato de `bloques.py`) |
| `proyectar_prov.py` | la noche: actas → proyección provincial, por sección y bancas |
| `ensayo.py` | ensayo general con una elección ya escrutada |
| `test_provincial.py` | pruebas (ingesta con nombres y sin padrón, bancas, cociente) |

## Uso

```
python -X utf8 proyeccion/provincial/ingestar.py pba2025          # cuando llegue el archivo de graficarpba
python -X utf8 proyeccion/provincial/ensayo.py --prov pba --destino pba2025 --origen 2023p --fuerzas FP,LLA,SB,FIT,OTRAS
python -X utf8 proyeccion/provincial/proyectar_prov.py actas.csv --prov pba --origen pba2025,2025bl --fuerzas FP,LLA,SB,FIT,OTRAS --antecesores ant.json --marco padron27.csv --anio 2027
python -X utf8 proyeccion/provincial/test_provincial.py
```

Actas: el mismo CSV de `proyectar_fotos.py` (`foto, seccion_id, circuito, mesa, completa, bloque, votos`;
`distrito_id` puede faltar). `seccion_id` es el código de partido de la DINE o su nombre. Orígenes: cualquier
`circ_<clave>.pkl` de `proyeccion/` o `transferencias/` (nacionales `2023p`, `2025bl`...) o una provincial
ingresada. Antecesores: los de `proyectar_fotos.ANTECESORES`, más los de `--antecesores` (JSON
`{"origen": {"BLOQUE": ["columna del origen"]}}`); un bloque con el mismo nombre en el origen es su propio antecesor.

## Verificación de las bancas (29-oct-2026)

- **Regla**: Ley 5109, arts. 109 y 110, texto actualizado en normas.gba.gob.ar (`VGW7pIWV`). Cociente Hare = votos de
  las listas / bancas, **sin blancos ni anulados**; las listas que no llegan al cociente no tienen representación; los
  restos, uno por lista a los mayores residuos; si todavía sobran, a la lista más votada (no otra vuelta, como estaba
  antes: corregido). Art. 110: si ninguna llega, el piso baja a la mitad hasta que alguna llegue; si llegan más listas
  que bancas, van a las más votadas.
- **Bancas por sección**: art. 13 (Capital 3/6, 1.ª 8/15, 2.ª 5/11, 3.ª 9/18, 4.ª 7/14, 5.ª 5/11, 6.ª 6/11, 7.ª 3/6
  senadores/diputados). La Ley 14.086 (50 y 100) fue observada por el Decreto 2997/09; las de 2023 y 2025 cierran con
  46 y 92.
- **Renovación**: 2025, senadores en 1.ª, 4.ª, 5.ª y 7.ª y diputados en 2.ª, 3.ª, 6.ª y Capital (Chequeado, El
  Economista); 2027 repite 2023: senadores en 2.ª, 3.ª, 6.ª y Capital y diputados en 1.ª, 4.ª, 5.ª y 7.ª.
- **Prueba**: con las provinciales 2023 por partido del catálogo de la provincia, la regla da las bancas de la
  Wikipedia en las ocho secciones (UxP/JxC/LLA: 1.ª 7/4/4, 4.ª 5/5/4, 5.ª 4/4/3, 7.ª 2/2/2 diputados; 2.ª 2/2/1,
  3.ª 5/2/2, 6.ª 2/2/2, Capital 2/1/0 senadores). Queda como test en `test_provincial.py`.

## Datos de la PBA 2025 por debajo del partido

Búsqueda del 29-oct-2026: no hay nada público por circuito ni por mesa de la elección del 7 de septiembre.
- El sitio del provisorio (`resultados.eleccionesbonaerenses.gba.gob.ar`, con mesa y telegrama) ya no resuelve, y
  el Wayback Machine estaba fuera de servicio al consultarlo: reintentar (`web.archive.org/cdx`, host con `*`).
- El catálogo de datos abiertos de la provincia (`catalogo.datos.gba.gob.ar`, API CKAN) tiene provinciales 2005–2023
  y nacionales 2011–2023 **por municipio**; nada de 2025. Las provinciales quedaron en
  `datos/provinciales/gba_catalogo/` y 2023 se ingresó como origen `pba2023` (por partido).
- La prensa (La Nación, Infobae, Perfil) publicó por sección y por municipio, no por circuito.

## Qué falta

- **PBA septiembre 2025 por mesa** (pedido a graficarpba): sin ese archivo no hay origen provincial de 2025 ni
  backtest provincia → provincia. Formato esperado en `datos/provinciales/pba2025/LEEME.md`. Mientras tanto,
  `pba2023` (por partido) sirve de origen provincial: las actas se comparan con su partido, no con su circuito.
- Otras provincias: agregar la entrada en `PROVINCIAS` (sin secciones electorales, la unidad es el departamento) y
  su elección anterior por mesa en `ELECCIONES`. Cada provincia publica en otro formato.
- Padrón 2027 por circuito para `--marco`; mientras tanto el motor usa los electores del primer origen.
- Las listas de 2027 y sus antecesores, cuando cierren las alianzas.

## Ensayo general

Mientras no llegue la provincial, se probó con lo que hay: **presidente 2023 (1.ª vuelta) → diputados nacionales
2025, solo la PBA**, 30 mesas, 100 colecciones por esquema, 300 remuestras (`ensayo_pba_2025bl_2023p.md` y `.csv`).
Prueba el circuito completo (sección electoral como unidad, repesado conurbano/interior, marco), no la calidad para
una elección provincial.

| Esquema | Error medio abs. del margen | Sesgo | Error medio por fuerza | Error por sección (2 primeras) | Cobertura LLA / FP / OTRAS |
|---|---:|---:|---:|---:|---:|
| azar | 1,55 | −0,24 | 0,55 | 1,36 | 99 / 97 / 94 % |
| 65 % conurbano | 1,71 | +0,40 | 0,60 | 1,54 | 97 / 96 / 89 % |

El margen real fue LLA +0,54: con un empate así el «ganador correcto» (53–66 %) no dice nada. Como en la nacional,
las colecciones de una misma elección no son elecciones independientes, y el esquema de selección extrema no se probó.

Con la **provincial 2023 por partido como origen** (`pba2023`, antecesores en `antecesores/pba2023_a_2025.json`:
LLA ← LLA + JxC, FP ← UxP, FIT ← FIT; PU sin antecesor), mismo destino y diseño (`ensayo_pba_2025bl_pba2023.md`):

| Esquema | Error medio abs. del margen | Sesgo | Error medio por fuerza | Error por sección (2 primeras) | Cobertura LLA / FP / OTRAS |
|---|---:|---:|---:|---:|---:|
| azar | 2,18 | −0,65 | 0,67 | 1,43 | 98 / 100 / 95 % |
| 65 % conurbano | 2,13 | +0,35 | 0,70 | 1,57 | 100 / 100 / 88 % |

Medio punto peor que con el origen por circuito (presidente 2023): es lo que se pierde al comparar cada acta con su
partido en vez de con su circuito. Por eso hace falta la provincial de 2025 por mesa.
