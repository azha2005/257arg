# Elecciones legislativas del 14 de octubre de 2001 (diputados nacionales)

`atlas_2001.html` (`python build_2001.py`; generado desde `mapa1997/build_1997.py`). Departamentos del censo de 1991 + partidos nuevos de 2001 + 28 circunscripciones de Capital. Modos: ganador, PJ, Alianza, ARI.

## Datos
- `Bases Ernesto/2001 x DTO/Diputados Nacionales/*.xls` (una planilla por provincia, las 24) procesado con `base8399/construir_dn2001.py` a `base8399/ernesto/2001_diputados/dpto_partidos.csv` (formato largo como las otras elecciones) + `mapeo_columnas.csv` (hoja `dn2001` de `agrupaciones/DN01.xls`: lista y grupo que Ernesto asignó a cada columna). 539 unidades.
- **Las planillas no traen nombres, solo el código `DTO`.** Los nombres salen de las bases de otros años por el mismo código INDRA, pero la numeración de algunas provincias cambia entre años: se eligió por provincia el año cuya numeración reproduce el orden de votos de 2001 (Spearman): San Luis 1993 (1995 daba −0,25) y Santiago del Estero 1995 (1997 daba 0,74); en el resto, 1997 (1999 tiene algún nombre cambiado, p. ej. Escobar). Control: mediana 2001/1997 de positivos = 0,89; los desvíos grandes que quedaron (Chubut 07003/07004, Jujuy 10008, Salta 17010) son unidades chicas con pocos o cero votos.
- Almirante Brown y General San Martín (Buenos Aires): una columna tiene 1.000 votos de más que no cierran con los positivos; se usa la suma de las listas y la tarjeta lo dice.
- Nacional: tabla de «Elecciones legislativas de Argentina de 2001» (`w2001.txt`, `../wikitop.py`; las tablas provinciales quedaron en `wiki_prov.json`, script `wprov2001.py`).

## Bloques (columna por columna, según los «Total» de la tabla)
Se partió del grupo de Ernesto con estas correcciones: **PJ = Concertación Justicialista** (PJ, Partido Nuevo, Unión por Córdoba con el UCeDé cordobés, Frente por un Nuevo País, Alianza de Centro, Compromiso Social, FUCAM, Frente con Todos de La Rioja, Frente para Todos de Tucumán, UCeDé de Tierra del Fuego); **Frente Unión por Buenos Aires** (Capital) fila aparte (Ernesto lo trae como PJ); ARI suma PSA, PI, PSD, PSP, Frente de la Gente; IU suma MST; UCeDé suma Unidos por Catamarca; Unidad Federalista (PAUFE) suma el Pacto de Unidad, Fe y Esperanza. Detalle en `OVERRIDE` y `GROUP2BLOC` del build.
Base vs. tabla: PJ 5.358.818 vs 5.499.353 (−2,6 %), Alianza 3.194.910 vs 3.244.891 (−1,5 %), ARI 1.276.172 vs 1.300.438 (−1,9 %), PAUFE −6,7 %, AR −1,3 %, FUBA −1,5 %, PD −0,8 %, MPN −0,4 %.
**La base trae menos votos que la tabla en todo el país**: 13.968.343 positivos vs 14.290.108 (−2,3 %). Por provincia contra la tabla provincial: 0 a −2 % en casi todas, Santiago del Estero −3,3 %, Salta −6,5 %. Parece un cómputo anterior al definitivo; no se corrigió.

## Geometría
Igual que 1997 (`../newpartidos.py`, partidos nuevos con polígono propio del shapefile de 2001) y además **San Salvador (Entre Ríos)**, que la base de 2001 trae aparte.

## Colores y logos
Colores de la Wikipedia: PJ #318CE7, Alianza #DC0143, ARI #6FB53E, PAUFE ámbar #f59e0b (la Wikipedia usa gris #808080, que se confundía con «otros» y con el voto bronca; cambiado el 19-oct-2026 a pedido del usuario, igual que en la variante con voto bronca), AR #3E5298, PD #1F2F6B, MPN #0070B8. Excepción: el Frente Unión por Buenos Aires lleva en la tabla el azul del PJ; se le dio #8DBDF2 para distinguirlo. Logos: PJ bandera cuadrada (el de la Concertación de Commons es de 2019), Alianza (1997), ARI (Commons, 2002, no verificado), AR (1997), PD, MPN; PAUFE y FUBA con sigla.

## Pendientes
- Paquete de Commons en `commons/2001/` (sin subir). No se comparó con el mapa vigente del artículo.
- 2001 no se agregó a `xlsx_resultados/` (`exportar_xlsx.py`).
