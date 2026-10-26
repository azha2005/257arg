---
name: atlas-proyecto-dataelecc
description: Flujo de este proyecto (dataeleccproyecto) para armar, corregir o regenerar un atlas electoral argentino por departamento (diputados nacionales u otros) y empaquetarlo para Wikimedia Commons. Usalo cuando el usuario pida un mapa/atlas de un año nuevo (p. ej. 1999, 2003), cambiar un color, un logo o la geometría de un año ya hecho, propagar un cambio a todos los atlas, o preparar la subida a Commons. Complementa a mapa-electoral-wikipedia-1999, que es la plantilla genérica.
---

# Atlas del proyecto dataeleccproyecto

Antes de hacer nada, leer `AGENTS.md` (raíz del proyecto): tiene las reglas fijadas por el usuario, los pasos, las trampas conocidas y la sección «Workflow completo de un atlas de diputados». Este skill es el resumen operativo; si algo no coincide, manda `AGENTS.md`.

## Orden de trabajo
1. Copiar el build más cercano (`mapa1994/`, `mapa1997/` o `mapa2001/`). No usar el proyecto 1976 como base.
2. Datos por departamento de `base8399/ernesto/<año>_<cargo>/dpto_partidos.csv`; el total nacional sale **siempre** de la tabla de Wikipedia (`wikitop.py`, `WIKI[año]`).
3. Mapear códigos a bloques y comparar «bloques según la base» contra «según Wikipedia».
4. Geometría de 1991 + `newpartidos.apply(...)`: los partidos nuevos tienen polígono propio, nunca se fusionan.
5. Colores de la Wikipedia; si chocan, el color fijo del proyecto (FR #7b3f00, MPN #14306e, PJ #318ce7, UCR #e10019). Mismo partido, mismo color en todos los años.
6. Provincia sin datos: `DATA.solid` con el total provincial, rotulado.
7. Build → mirar todos los modos → `render_transparentes.py` → `render_blanco.py <carpeta> <html>` y copiar a `png_transparentes/all elections white bg/`.
8. Commons: `commons/config.py`, `python commons/paquete.py <año>`, `python commons/chequeo.py`.
9. LEEME del año, nota en `AGENTS.md` y memoria.

## Reglas que no se discuten
- Leyenda solo con partidos que ganan al menos una unidad; lo no conseguido queda beige y rotulado, nunca imputado.
- Logos de época; sin uno, el más cercano anotado como no verificado en `logos_wikipedia/LICENCIAS.md`.
- Un cambio compartido (color, geometría) se propaga a todos los años afectados y se avisa cuáles paquetes de Commons hay que resubir.
- Decir con claridad qué se verificó mirando y qué no.

## Comandos
```
python mapa<AÑO>/build_<AÑO>.py
python render_transparentes.py
python render_blanco.py mapa<AÑO> atlas_<AÑO>.html
python commons/paquete.py <año> && python commons/chequeo.py
```
