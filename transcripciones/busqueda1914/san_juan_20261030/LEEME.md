# San Juan 1914: transcripción territorial y control de 114 mesas

30-oct-2026. Transcripción visual del expediente HCDN19-P-1914 ya descargado en `../fuentes/san_juan_19-p-1914.pdf`,72 páginas. No es una fuente recién descubierta: son **datos nuevos extraídos de una fuente pendiente de lectura**. No se modifican atlas ni consolidado principal todavía.

## Elección y unidad

La portada PDF5 dice elección de un diputado nacional del22 de marzo de1914. Oficio PDF3,17/4/1914, remite30 fojas y nombra a Roberto Barrera como electo. La Junta se constituye para escrutar el23/3 (PDF7). PDF17 identifica explícitamente los colegios del1.º,2.º y3.º distrito como pertenecientes a la sección electoral de Capital. Se conservan esos rótulos literales, sin trasladarlos a circunscripciones de Capital Federal ni a límites de otro año.

## Resultado tangible

`mesas_capital.csv`: **16 mesas admitidas**,15 de22/3 y la complementaria de5/4, con Barrera y Marcial V. Quiroga leídos en cada mesa. Sus sumas se guardan en `control.json`. El1.º distrito tiene7 mesas, el2.º4 y el3.º5.

PDF23 anula la mesa4 del3.º distrito por veinte sobres de diferencia en más. **No contiene cifra de votos por candidato recuperable allí**; no se agrega la urna anulada. PDF63 fecha la sesión6/4 y dice que las complementarias de esas dos mesas tuvieron lugar el5/4. PDF64 publica Capital3.º/mesa4: Barrera94, Quiroga2, blancos2; Angaco Norte/mesa2: Barrera109, Quiroga3, blancos1. No menciona Soldati en esas dos mesas: sus celdas siguen vacías.

La transcripción es por candidato, no por lista ni electores presidenciales. Barrera y Quiroga están explícitos en todas las16 mesas recuperadas de Capital. La columna de Soldati contiene **14 menciones**, con dos silencios; no presentar su suma observada como total departamental certificado. En Capital3.º/mesa1 aparece dos veces el mismo candidato: cuatro votos y luego «uno idem por el mismo Sr Soldati» (PDF21–22), registrados5=4+1 con nota. Esta anomalía requiere cotejo con planilla original antes de integración. Tampoco se convierten en cero los blancos/dispersos no mencionados.

## Control con el cierre provincial

Acta general6/4 (PDF67–72). PDF69 publica Barrera10.194, Quiroga3.187, Fernando Soldati202, diversos ciudadanos17, blancos155: suma13.755. Es control provincial del expediente, **no repartirlo entre departamentos**. PDF70 refiere112 urnas de22/3 y2 de la complementaria del día anterior. PDF68 lista los colegios provinciales; confirma que el manuscrito contiene mucho más territorio por transcribir.

## Evidencia y límites

Imágenes revisadas: PDF17–24,63–64 y portada/fechas PDF3/5/7, resumen PDF67–72. Renders y ampliaciones de lectura en `analisis/wikipedia_library_20261030/sj1914_pdf*.png`. El original oficial está en `transcripciones/busqueda1914/fuentes/san_juan_19-p-1914.pdf`. No usar el OCR para fijar cifras manuscritas. Resta una segunda transcripción de las cifras y completar los demás colegios; no declarar San Juan entero recuperado.

Primeras reservas gráficas: nombres de dispersos en Capital2.º/mesa1 se conservan aproximados en notas, sin normalizar identidades. Capital1.º/mesa3 Barrera86 verificado en ampliación; Capital1.º/mesa6 Soldati13. Los votos de candidatos dispersos no se mezclan con Marcial V. Quiroga aunque compartan apellido.

## Continuación: Trinidad y Desamparados

`mesas_trinidad_desamparados.csv`,17 mesas adicionales; `control_trinidad_desamparados.json` conserva sumas y número de menciones. Lectura visual PDF25–31 del mismo expediente:

| Colegio electoral literal | Mesas | Barrera | Quiroga | Soldati |
|---|---:|---:|---:|---:|
|Trinidad|8|754|266|43|
|Desamparados|9|849|173|12 observados en6 mesas; no total completo|

PDF25 enumera las ocho mesas de Trinidad; PDF28 enumera las nueve de Desamparados. Cada una aparece luego con cifras expresas para Barrera y Quiroga. No se nombran departamentos modernos ni se aplica geometría todavía. Son comicios nacionales22/3/1914, no la elección presidencial/legislativa1916.

**Corrección de lectura verificada:** Quiroga en Trinidad mesa6 lleva46. El número está sobre raspado en PDF27; la certificación del secretario en PDF31 salva expresamente «Sobre raspado = cuarenta y seis = vale». Se sustituyó la lectura preliminar45 antes de cerrar la entrega. Imagen de comprobación `sj1914_trinidad_mesa6.png`. Este voto hace que Quiroga sume266, no265.

En Desamparados mesas5/7/9 no se menciona Soldati; no se completa con ceros. Tampoco hay blancos expresos en todas las mesas. La cifra97 de Barrera/Desamparados6 está partida entre PDF29 («noven…») y30 («ta y siete»). El acta continúa hasta las firmasPDF31, que sólo salvan el raspado descrito.

Cobertura acumulada de esta tanda:33 mesas de Capital/Trinidad/Desamparados, más Angaco Norte2 complementaria en otroCSV. Mantener aparte los estados y no presentar aún una suma provincial completa. Resto de colegios desde PDF33 pendiente de transcripción.

## Segunda ampliación: Santa Lucía, Alto de Sierra y9 de Julio

Leído PDF33–35: sesión24/3/1914. Encabezado enumera cuatro mesas de Santa Lucía y sendas urnas únicas de Alto de Sierra y9 de Julio. Incorporadas en `otras_mesas.csv`, conservando el colegio literal.

| Colegio | Mesas | Barrera | Quiroga |
|---|---:|---:|---:|
|Santa Lucía|4|405|126|
|Alto de Sierra|1|136|57|
|9 de Julio|1|70|3|

Santa Lucía: pares99/31,107/23,98/46,101/26. Soldati sólo está mencionado en mesas1/2 (4/2); no declarar6 como total completo. El acta incluye Alto de Sierra y9 de Julio a continuación de Santa Lucía, pero **no se agregan geográficamente a ella**. Se mantienen tres rótulos distintos hasta homologación histórica.

`cobertura_acumulada.json` verifica40 claves de mesa únicas en los tresCSV:23 nuevas respecto de la entrega anterior, que tenía16 de Capital y1 complementaria de Angaco Norte. Ninguna complementaria se duplica con una urna anulada. La provincia sigue incompleta. PDF36 inicia Concepción (diez mesas y una de Chimbas): no transcrita en esta tanda.

## Continuación vigente: las 114 mesas del expediente

Actualización posterior del30/10/2026. **Este apartado y `control_provincial.json` sustituyen los recuentos parciales anteriores.** Se leyeron PDF35–62 y se agregaron74 mesas en `mesas_resto_provincia.csv`. Cobertura:114 claves únicas,112 del22/3 admitidas y2 reemplazos del5/4; no se agregan las dos urnas anuladas originales. PDF11 tipografiado confirma114 mesas originales,2 anuladas y2 complementarias; PDF70 explica112 originales escrutadas más2 complementarias.

Se completó la lectura de las mesas de los siguientes colegios literales, con cifras expresas para Barrera y Quiroga en cada una. Es cierre de cobertura de ambos candidatos por colegio en este expediente, **no homologación geográfica ni conciliación definitiva del total provincial**. Las sumas se calculan, no se atribuyen como subtotales escritos por la Junta:

| Colegio | Mesas | Barrera | Quiroga | PDF |
|---|---:|---:|---:|---|
|Concepción|10|906|307|35–38|
|Chimbas|1|118|30|39|
|Pocito|6|584|275|39–40,47–48|
|Rivadavia|3|255|118|42–43|
|25 de Mayo|3|211|38|43|
|Caucete|9|1003|63|44–46|
|Cieneguita|1|36|33|49|
|Cochagual|2|74|31|49|
|Berros|1|37|35|49|
|Retamito|1|57|1|49–50|
|Albardón|5|459|294|50–51|
|Ullum|1|46|21|51|
|Angaco Sud|4|300|117|51–52|
|Angaco Norte, incl. complementaria|4|441|75|52,63–64|
|Villa de Jáchal|4|227|231|53|
|Pampa Vieja|2|139|69|53–54|
|Huaco|2|141|82|54|
|Mogna|1|67|23|54|
|Rodeo|3|355|20|59|
|Valle Fértil|2|179|63|59–60|
|Barrial|1|88|7|61|

**Pocito6 resuelto:** la Junta aplaza el escrutinio por protesta sobre el suplemento del registro (PDF40–41), obtiene informe y admite la elección el25/3, con Barrera88/Quiroga33 (PDF47–48). No fue complementaria y no debe dejarse fuera ni duplicarse.

**Encabezado corregido:** las nueve mesas de PDF44–46 son **Caucete**, ver ampliación `sj1914_encabezado_pdf44.png`. Una lectura inicial provisional las llamó Jáchal; corregida antes de entregar los datos. Las cuatro de Villa de Jáchal están expresamente identificadas en PDF53 y no se mezclan con aquellas.

**Bloque territorial pendiente:** PDF57–58, sesión26/3, enumera cinco mesas y da Barrera467/Quiroga238; el encabezado consultado no nombra colegio. Se guardan como `Colegio sin identificar acta26marzo`. La lista de colegios de PDF68 menciona Pampa del Chañar, pero **no se le asignan estas cinco mesas por descarte**. Hace falta la planilla o el padrón para identificarlo.

Iglesia: dos mesas con Barrera130/90; Astica: Barrera90; Calingasta: Barrera207. En esas cuatro mesas Quiroga no está mencionado: sus celdas permanecen vacías. Las salidas de suma observada pueden mostrar0 con cero menciones; **no significa cero votos documentado**. Control explicita ambas magnitudes. Otros candidatos dispersos quedan en notas, y Soldati/blancos sin mención siguen vacíos.

### Segunda lectura y discrepancias sin corregir por residuo

Revisión de Capital PDF17–24, Trinidad/Desamparados PDF25–30 y ampliaciones de Concepción/Cieneguita. Correcciones sobre la entrega anterior: Trinidad3 Barrera95 (no99), Trinidad5 Soldati12 (no11), Desamparados8 blancos2. Trinidad queda **750/266/44**, ocho mesas con mención de los tres candidatos. Esos valores sustituyen754/266/43 de arriba. La segunda lectura corrigió también cifras preliminares de Concepción en el nuevoCSV, con notas por mesa.

| Categoría | Suma observada de mesas | Mesas con mención | Resumen provincial PDF69 | Diferencia |
|---|---:|---:|---:|---:|
|Barrera|10288|114|10194|+94|
|Quiroga|3174|110|3187|−13|
|Soldati|209|44|202|+7|
|Blancos|153|75|155|−2|

PDF69 manuscrito y PDF11 resumen tipografiado confirman10194/3187/202/17/155. **La diferencia de Barrera es exactamente94, su cifra en la complementaria de Capital3/mesa4.** Es pista de una posible omisión en el resumen o de otro problema de cómputo; no se afirma causalidad ni se altera la fuente. Las filas incluyen ese reemplazo una sola vez y ninguna urna anulada. Quiroga tiene cuatro silencios que no se rellenan con los13 de diferencia. Soldati tiene una suma observada mayor que el final y numerosos silencios: requiere cotejo posterior; no se resta7 arbitrariamente. La anomalía cuatro+uno para el mismo Soldati en Capital3/mesa1 se conserva.

Reproducir con `python transcripciones/busqueda1914/san_juan_20261030/controlar_cobertura.py`. Produce `control_provincial.json`, actualiza `cobertura_acumulada.json` y el control de Trinidad/Desamparados. Verifica114 claves únicas, dos complementarias y ausencia de las dos mesas originales anuladas. Este control de estructura/sumas no sustituye una segunda transcripción independiente completa.

Estado: varios colegios dejaron de carecer de cifras territoriales; se completó la cobertura de mesas del manuscrito. **Provincia aún no conciliada, cinco mesas sin identificación territorial y categorías sin mención.** No se modifica el atlas ni el consolidado principal hasta resolver estos puntos.
