# Actas de la carpeta «actas 18 a 19 hs»

Proyección retrospectiva de diputados nacionales 2025, hecha el 28-oct-2026. El conjunto proviene exclusivamente de esa carpeta; no incorpora las 27 mesas de `fotos25/` de la prueba anterior.

De 60 archivos, se identificaron 8 copias idénticas, 16 imágenes adicionales de mesas ya fotografiadas y 6 imágenes que quedan fuera para revisión o corresponden a voto en el exterior. Se incorporaron **30 mesas únicas en 28 circuitos**: 29 completas y una parcial. El detalle archivo por archivo está en `estado_imagenes.csv`; las imágenes secundarias de una mesa no cuentan otra vez. La carpeta contiene imágenes obtenidas desde X: la hora inferida de los identificadores de imagen es orientativa y no prueba por sí sola la hora exacta de publicación del tuit.

El CSV de entrada se armó mediante lectura manual de las imágenes, agrupando listas en los mismos bloques de la proyección. `transcribir.py` guarda esos valores explícitos y genera `actas.csv`. Las filas vacías de la mesa parcial no se interpretaron como votos cero. El contraste `control_provisorio.csv` es posterior y no reemplaza cifras de las fotos; la base se usó también para resolver identificadores geográficos cuando faltaban o eran ambiguos. En particular, Misiones mesa 72 no mostraba sección/circuito y se la ubicó mediante el registro; Corrientes 2130 muestra una sección dudosa y se usó la del registro. Esas identificaciones dependen de esa comparación retrospectiva.

Hay diferencias que no se corrigieron automáticamente: Córdoba mesa 5023 muestra 70 votos de Provincias Unidas y el provisorio registra 10; en Corrientes 2130, la foto muestra 2 blancos y el provisorio 8; en La Pampa 525 difieren las categorías no positivas. Córdoba 1158 difiere en un voto de OTRAS. Conservar la fotografía como fuente no resuelve si una discrepancia es un error del acta, de su lectura o de la carga oficial. Por eso también se corrió el escenario `actas_sin_cordoba_5023_proyeccion.md`: el margen cambia de +9,5 a +9,3 puntos. Las transcripciones son agrupadas y requieren nueva revisión visual antes de tratarlas como definitivas.

La corrida principal `actas_proyeccion.md` promedia antecedentes de presidente 2023 y diputados 2021, repesa AMBA/resto y ajusta votos provinciales y bancas conjuntamente. LLA 41,7 %, FP 32,2 %, PU 9,6 %, FIT 4,0 % y otras 12,6 %; margen LLA +9,5 puntos, contra +7,1 del provisorio disponible. Cinco mesas son del AMBA; la ponderación no corrige necesariamente el sesgo de selección de fotos. Las bandas y frecuencias son condicionales al modelo, no una garantía de cobertura para publicaciones seleccionadas.

Para reproducir:

```powershell
python -X utf8 proyeccion/fotos_18_19/transcribir.py
python -X utf8 proyeccion/proyectar_fotos.py proyeccion/fotos_18_19/actas.csv --origen 2023p,2021bl --real 2025bl --congreso 2025
```

Las imágenes `contacto_*.jpg`, `detalle_*.png` y `ampliada_*.png` son auxiliares locales de lectura; los originales permanecen intactos en la carpeta del usuario.
