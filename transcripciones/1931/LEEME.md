# Fuentes para 1931 (presidente y diputados, 8 de noviembre de 1931)

Relevamiento del 3-nov-2026. Arranca de la charla con Faustino Sojo: su intento de mapa de 1931 completa algunas provincias con las elecciones provinciales del mismo día, y dice que hay actas de la Cámara de Diputados con las presidenciales.

**Cantón no publica 1931 por departamento.** Lo omitió adrede por presunción de fraude. El tomo I (cap. III, PDF 186-187) trae solo los totales provinciales.

## Expedientes de la HCDN

Hay 13 expedientes citados en «Elecciones legislativas de Argentina de 1931» (`wleg1931.txt`). Están bajados en `expedientes_hcdn/`. Son los diplomas de diputados y traen una copia del acta de la junta escrutadora.

| Exp. | Distrito | Qué trae | ¿Presidente por departamento? |
|---|---|---|---|
| 113-D (96 pp.) | Mendoza | Acta de escrutinio mecanografiada, mesa por mesa y departamento por departamento. Ver la p. 31: Guaymallén. | **Sí.** Trae los electores de presidente por partido en cada departamento, además de diputados y gobernador. |
| 67-D (85 pp.) | La Rioja | Acta mecanografiada, circuito por circuito y mesa por mesa. | **Sí, por mesa.** Trae electores de presidente, diputados, gobernador y diputados provinciales. Hay que sumarla por departamento. |
| 65-D (13 pp.) | Jujuy | p. 3: «Cómputo general de votos para diputados nacionales», 14 departamentos (es la imagen que mandó Faustino). pp. 5-12: acta mecanografiada. | Diputados por departamento, sí. Electores: falta mirar las pp. 5-12. |
| 48-D (31 pp.) | Santa Fe | Acta impresa. Lo nacional va solo en total provincial. | No. Lo que viene por departamento (pp. 13-19) es la **elección provincial**: electores de gobernador, senador y diputados. Sirve como aproximación (Alianza contra Concordancia). |
| 40-D (9 pp.) | San Juan | Lo nacional en total provincial. | No. La legislatura provincial va por circunscripción y departamento (p. 3): sirve como aproximación. |
| 60-D | Buenos Aires | Acta general de proclamación. | No, solo totales. |
| 43-D | Córdoba | Proclamación. | No, solo totales. |
| 44-D | Corrientes | Proclamación. | No. |
| 47-D | Entre Ríos | Proclamación. | No. |
| 34-D | Santiago del Estero | Proclamación. | No. |
| 53-D | San Luis | Proclamación y nota. | No, a primera vista. |
| 86-D | Catamarca | Impugnación mecanografiada. | Falta revisar si nombra departamentos con cifras. |
| 81-OV-1932 | Santa Fe | Elección complementaria de 1932. | No corresponde a 1931. |

**Hay más expedientes de 1931.** `expedientes_existentes_hcdn.txt` lista los que respondían HTTP 200 el 3-nov-2026: unos 110 de la serie `n-d-1931`, uno por diputado electo, más algunos de 1932. Varios pesan como el de Mendoza y pueden traer otra copia completa del acta, quizás de otro distrito:

- 89-D, 114-D, 115-D, 116-D y 117-D: unos 31-33 MB cada uno.
- 54-D, 83-D, 111-D y 128-D: unos 5 MB cada uno.

Interesan sobre todo los de Capital, Tucumán y Salta, que Wikipedia no cita.

**Ojo:** después de sondear unas 370 URL en paralelo, la HCDN pasó a responder **403**. Para seguir:

- Bajar de a uno y con pausas.
- O usar la Wayback Machine (`web.archive.org/web/2022id_/https://apym.hcdn.gob.ar/...`).

## Prensa

- **Hemeroteca Digital de Santa Fe** (*El Orden*, *El Litoral*, *Diario Santa Fe*, nov.-dic. de 1931). Es la fuente de los cierres provinciales del artículo de Wikipedia. Según Faustino, está en mantenimiento. Los números de diario están en `wleg1931.txt`.
- **La Prensa (Buenos Aires):** Internet Archive no tiene ejemplares de 1931 con el patrón `LaPrensa_BuenosAires_1931*`. NewspaperARCHIVE (Wikipedia Library) la cubre solo hasta 1928.

## Siguiente paso sugerido

1. Transcribir Mendoza (113-D) y La Rioja (67-D): son presidente por departamento, directo.
2. Mirar Jujuy 65-D, pp. 5-12, por si traen los electores.
3. Identificar los expedientes grandes no citados, cuando la HCDN deje de bloquear.
4. Santa Fe y San Juan: decidir si se usan las provinciales como aproximación, rotuladas como tal (regla 8: no imputar sin decirlo).
