# Transcripción de diputados nacionales 1918 y 1920

Fuente: Darío Cantón, *Materiales para el estudio de la sociología política en la Argentina* (1968), tomo II; PDF local `raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf`. SHA-256 conservado en los controles. Encabezados: varones solamente.

| Año | Páginas PDF (desde 1) | Páginas impresas | Distritos | Filas | Celdas | Números | Marcas |
|---|---|---|---:|---:|---:|---:|---:|
| 1918 | 44–54 | 35–45 | 8 | 259 | 1.325 | 968 | 357 |
| 1920 | 56–68 | 49–61 | 10 | 278 | 1.374 | 939 | 435 |

1918 cubre Capital, Buenos Aires, Catamarca, Córdoba, Corrientes, Entre Ríos, Mendoza y Santa Fe. 1920 cubre Capital, Buenos Aires, Córdoba, Corrientes, Entre Ríos, Jujuy, Mendoza, San Luis, Santa Fe y Tucumán. Son las tablas que publica el tomo: no afirmar cobertura nacional por tener todas esas páginas transcritas.

Dos subagentes Terra hicieron una primera lectura visual en paralelo. Después el principal revisó claves desvanecidas, lecturas dudosas, anomalías seleccionadas y discrepancias con Lupu–Stokes. Véase [REVISION.md](REVISION.md): distingue lo revisado de lo pendiente.

**Reservas antes de mapear:** queda ilegible un padrón de Capital 1918; Balcarce 1918 conserva un dígito de lectura débil; y el propio libro cita 1922 para partidos en Capital/Santa Fe 1918 y 1924 para votantes en Capital 1920. Esas fechas se conservan con alerta y requieren cotejo primario. No se completó ninguna cifra con otra base ni por residuo.

## Archivos por año

En `../canton1918/` y `../canton1920/`:

- `canton_<año>.json`: documento canónico por página, con columnas originales, marcas, fuentes impresas y reservas cronológicas.
- `canton_<año>.csv`: una celda por registro, valor o marca, página PDF e impresa; `origen_marca` distingue asterisco general de encabezado y marca individual.
- `TRANSCRIPCION_<año>.md`: tablas legibles, con claves y reservas por página.
- `CONTROL_<año>.json`: conteos, hash, sumas por columna y distrito, alertas aritméticas y filas parciales.
- `DIFERENCIAS_ORIGINAL_<año>.md`: diferencias aritméticas conservadas, sin ajustes.
- `COTEJO_LUPU_<año>.json`: coincidencias y diferencias diagnósticas entre subconjuntos de columnas y familias académicas, sin usarlo como equivalencia partidaria.
- `manual<año>.txt`, `NOTAS_FUENTES.md` y `DUDAS.md`: registro de lectura, fuentes y dudas iniciales con su resolución.

`*` es sin dato; `**` es incluido en otra unidad o no considerado, según la nota del autor. Ninguno equivale a cero. Una columna marcada en el encabezado puede no tener asteriscos impresos en cada fila; se distingue esa procedencia en los archivos exportados. Inscriptos/votantes omitidos no se infieren de la suma de partidos.

## Reproducir las entregas

Desde la raíz del proyecto:

```powershell
python transcripciones/canton1918_1920/revisar.py
python transcripciones/canton1918_1920/exportar.py
python transcripciones/canton1918_1920/cotejo.py
```

Los JSON por año son la entrada canónica; el exportador no ejecuta OCR. `revisar.py` aplica idempotentemente las cuatro correcciones/resoluciones de la segunda lectura y las notas de fuente. Las imágenes de trabajo no se publican. El cotejo no modifica la base.

Entrega local de transcripción: sin cambios en atlas, publicación, paquetes de Commons ni memoria personal.

Por pedido posterior del usuario se construyeron los atlas locales de 1918 y 1920 desde estas transcripciones, preservando sus reservas. La base canónica permanece sin cambios. Véase `../entreguerras/LEEME_1918_1920.md` para las agrupaciones de Wikipedia, cartografía y validación de los mapas.
