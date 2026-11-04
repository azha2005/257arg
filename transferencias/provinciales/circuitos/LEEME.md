# Ampliación territorial de provinciales 2023 y 2025

2 de noviembre de 2026. Esta carpeta conserva fuentes, correspondencias explícitas y 27 cruces adicionales. Se suman al visor sin borrar los 25 cruces anteriores, que sirven como referencia a mayor agregación. El selector prioriza la versión con más unidades utilizables.

## Qué se incorporó

| Provincial | Comparación con presidente general 2023 | Empalme |
|---|---:|---|
| Buenos Aires 22/10/2023 | 1.042 circuitos | Provisorio DINE, gobernador y presidente simultáneos, mesas nativas |
| CABA 22/10/2023 | 167 circuitos | Provisorio DINE de jefe de Gobierno, simultáneo con presidente |
| Catamarca 22/10/2023 | 157 circuitos | Provisorio DINE de gobernador, simultáneo con presidente |
| Chaco 17/09/2023 | 152 circuitos/uniones | Definitivo provincial, códigos y pertenencia territorial contrastados |
| Santa Fe 10/09/2023 | 70 unidades | Distritos provinciales donde cierra el empalme; departamentos completos en el resto |
| Salta 14/05/2023 | 284 subcircuitos | Planilla definitiva; sólo positivos y blancos, sin nulos ni abstención |
| Misiones 07/05/2023 | 75 unidades | Municipios observados y circuitos nacionales agrupados; Iguazú completo por códigos sin correspondencia |

Cada provincial de 2023 tiene además origen presidente 2019 y destino balotaje 2023, con su cobertura particular. La serie 2023 pasa a nueve distritos: los cuatro originales más Chaco, Santa Fe, Buenos Aires, CABA y Catamarca. **Un cruce entre cargos simultáneos no observa una transferencia temporal**; informa una asociación ecológica entre composiciones territoriales de dos categorías.

En 2025 se agregan Chaco (152 unidades), Corrientes (172 circuitos, para sus tres cargos), Misiones (75 unidades) y Santa Fe (70). CABA, Jujuy y Salta ya tenían circuitos/subcircuitos; Buenos Aires sigue por municipio. Formosa sigue pendiente de descarga y validación; no se rellenó.

## Reglas de empalme

1. Los IDs internos de un API no son códigos electorales. Chaco usa claves internas como 1595; se toma el código electoral 1 de su descripción. Corrientes distingue del mismo modo el `valor` de filtro y el código de circuito.
2. Código y departamento se cotejan juntos, con alias explícitos de nombres. No hay búsqueda difusa. Los resultados nacionales proceden de los caches DINE y sus nombres se extraen de los originales por mesa, sin emparejar personas ni números de mesa entre elecciones.
3. Una unidad completa de origen no se cruza con una parte de destino. Si no se puede completar un empalme interno, se agregan unidades enteras de ambos lados hasta la misma área o se excluye el dato.
4. Los cruces 2019→2023, salvo Santa Fe con tabla CNE, tienen control adicional del padrón: razón 2023/2019 dividida por el crecimiento mediano; se excluyen claves fuera de 0,75–1,33. El CSV registra cada clave. Esto detecta cambios fuertes, pero **no certifica límites históricos**. Un circuito con código y padrón similares todavía puede tener modificaciones internas. Las versiones departamentales anteriores se conservan para evaluar ese límite.

## Chaco

Fuente de resultados: API pública del visor del Tribunal, elecciones 3 (2023) y 15 (2025). Se descargaron todos sus circuitos; los totales por fuerza y no positivos cierran exactamente con el resumen oficial. En 2025 hay 159 códigos en el catálogo y 153 con resultados; los seis restantes están reflejados en otros según aviso expreso del propio visor.

El [catálogo territorial del Tribunal del 09/04/2019](https://electoralchaco.gov.ar/384-circuitos/) documenta La Eduvigis en 31, 58 y 59, y Cote Lai en 36 y 68, a través de límites departamentales. Se usan esas uniones completas en ambos lados. También se unen 24/25, 32/35, 54/56 y 115/116. No se cambian votos entre circuitos ni se asigna todo a un departamento nacional por el rótulo municipal del API. El resultado de la unión es 152 unidades.

2023 general: 100 % de la fuente provincial cruzada. Balotaje: 148 unidades y 98,717 %, por circuitos nacionales sin votos informados. 2019: 146 unidades y 98,321 % tras el control de padrón. 2025: 152 y 100 %.

## Corrientes

La lista oficial trae 173 circuitos. Se cotejó el título de cada resultado, no sólo la descripción del menú, contra los nombres DINE. 164 títulos son compatibles directamente; seis de Capital tienen un título genérico y se admiten con código coincidente y padrón compatible; tres tienen variantes explícitas de abreviatura/ortografía (27, 37A y 89). El CSV conserva títulos completos y ambos padrones. En esos nueve casos la razón nacional/provincial está entre 0,967 y 1,009.

Circuito 62: sin votos nacionales informados, excluido. Quedan 172 circuitos con cobertura provincial aproximada del 99,928 %. Los totales por circuito coinciden con el resumen general de alianzas; las diferencias mínimas respecto a la suma departamental del propio API se conservan sin ajustar (8 votos en diputados, 10 en gobernador, 9 en senadores).

## Santa Fe

Los ODS oficiales 2023 y 2025 publican gobernador o convencionales por **distrito/localidad**. No son resultados observados por cada circuito nacional dentro de las ciudades. Santa Fe y Rosario están agregadas bajo código 9999; no se equipara ese 9999 con un circuito nacional.

Se contrastan localidad, código y departamento usando los nombres nacionales de 2025. Para 2019 se reutiliza la tabla documentada CNE 66/2022 del proyecto. Algunos nombres rurales y barrios no tienen correspondencia municipal completa. En esos departamentos se agregan **todos** los resultados provinciales y nacionales; no se comparan municipios completos con subconjuntos de circuitos. Sólo los departamentos donde cierra el empalme conservan sus distritos menores. Quedan 70 unidades comunes con toda la fuente provincial, frente a 19 del cruce previo. Los CSV conservan tanto candidatos nominales como las reservas del agrupamiento final.

## Misiones

Fuente territorial: [mapa oficial de abril de 2023](https://www.electoralmisiones.gov.ar/wp-content/uploads/2023/04/Circuitos-Mnes-2023-Completo.pdf), con códigos por municipio y tablas de electores. Los 78 resultados municipales del definitivo 2023 y la publicación estadística 2025 se conservan tal como estaban extraídos y verificados.

`misiones_municipios.py` declara cada circuito y municipio, sin deducir pertenencia de prefijos. Los circuitos nacionales se suman por municipio. Cuando aparece un código sin correspondencia o un municipio sin unidad equivalente previa, se agrega todo el departamento en ambas elecciones. Así, Iguazú se agrega en 2023/2025; Guaraní se agrega hacia 2019, porque Fracrán no tiene unidad separada en esa base. El mapa advierte que los límites municipales de Fracrán están sujetos a modificaciones: esa reserva se mantiene.

2023 general: 75 unidades y cobertura municipal completa; balotaje: 74 y 99,175 %. Hacia 2019: 76 unidades y cobertura municipal completa. 2025: 75 unidades completas. Las diferencias internas de publicación (495 votos no municipales en 2023 y 11 de discrepancia en 2025) siguen documentadas en el LEEME principal; no se ajustan.

## Salta

La planilla 2023 contiene 325 subcircuitos, además de resoluciones sin código. Se empalman dentro del departamento, no se reutilizan números de mesa. General presidencial: 284 utilizables, 98,942 % de los válidos provinciales; balotaje: 277 y 98,440 %. Hacia 2019: 270 y 96,075 % después del control conservador del padrón. El recorte puede variar porque el provisorio nacional no informa votos en algunos códigos.

Sáenz y Avancemos siguen separados; Avancemos no permite aislar el voto propio de Ahora Patria. Los nulos y la abstención quedan fuera de esta versión fina porque la planilla no los desglosa por subcircuito. El cruce departamental con padrón verificado sigue disponible.

## Búsqueda que no habilitó un empalme más fino

- Río Negro 2023: el portal tiene 88 localidades, 310 establecimientos y 1.802 mesas. Sus ocho circuitos legislativos regionales no son los circuitos nacionales. La fuente oficial también documenta rediseños del voto parroquial en 2023. Falta una correspondencia suficiente entre las unidades electorales de ambas elecciones; se conserva el cruce departamental.
- Neuquén 2023: el definitivo por mesa y su distribución provincial distinguen 146 etiquetas de circuito/localidad. Los nombres DINE 2023 son códigos numéricos; falta la tabla territorial que permita resolver la equivalencia con las subdivisiones nacionales. No se emparejaron mesas por su número.
- Misiones 2023/2025: no se obtuvo un definitivo provincial por circuito; la mejora válida consiste en agregar los nacionales a los municipios observados, con las reservas anteriores.
- Córdoba y Mendoza 2023: se identificaron portales, pero no se recuperó y validó una base territorial de esos comicios en esta ampliación. No se incorporan por una referencia de prensa o por totales provinciales.
- Buenos Aires 2025: la fuente definitiva recuperada sigue siendo municipal. No se inventa un reparto por circuito.
- Formosa 2025: descargas oficiales aún pendientes.

## Reproducir

```powershell
python -X utf8 transferencias/provinciales/circuitos/investigar.py
python -X utf8 transferencias/provinciales/circuitos/fuentes2023.py
python -X utf8 transferencias/provinciales/circuitos/nombres_nacionales.py
python -X utf8 transferencias/provinciales/circuitos/extraer_api.py
python -X utf8 transferencias/provinciales/circuitos/extraer2023.py
python -X utf8 transferencias/provinciales/circuitos/auditar_correspondencias.py
python -X utf8 transferencias/provinciales/circuitos/empalmar.py
python -X utf8 transferencias/provinciales/estudio.py
python -X utf8 transferencias/provinciales/construir_visor.py
python -X utf8 transferencias/provinciales/verificar.py
```

Se conservan las mismas dos variantes, 200 remuestreos y criterios de incertidumbre. Más unidades no aseguran identificar mejor cada fila: la heterogeneidad local puede aumentar. Los resultados son inferencias ecológicas, no seguimiento individual. `CONTROL_EMPALMES.json`, las correspondencias y `VALIDACION.json` permiten revisar el resultado concreto. Sin publicación externa.

Verificación final: 52 matrices con conservación, no negatividad y filas normalizadas; 52 gráficos con etiquetas dentro del área y sin solapes; ambas variantes y selección de orígenes/destinos funcionales; descargas SVG, PNG y CSV probadas. El estilo Ink se mantiene, sin eyebrows; Hallmark da 0 FAIL, 0 REFLEX y 0 WARN, con la excepción ya documentada de los neutros del tema.
