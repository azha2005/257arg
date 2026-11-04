# Protocolo fijado antes de evaluar PASO 2021

28-oct-2026. Se reserva diputados nacionales PASO del 12-sep-2021. Se conserva el software previo en `../congelado_20261028/`, con manifest y ZIP SHA256. Este es un experimento retrospectivo con aislamiento de información, no una predicción hecha en 2021. El diseño y la arquitectura ya fueron influidos por elecciones posteriores; ninguna prueba actual puede borrar ese conocimiento. Israel aporta una prueba de transportabilidad entre sistemas electorales, no sustituye la validación temporal argentina.

## Separación de funciones e información

El preparador puede leer los CSV oficiales y producir: marco con claves/electores, catálogo de nombres y resultados sellados. No imprime ni calcula porcentajes nacionales de PASO 2021 durante la preparación. El predictor recibe únicamente resultados históricos hasta 2019, marco de 2021 sin votos y exactamente 30 actas reveladas por muestra. El evaluador separado abre los resultados totales solo después de guardar las predicciones y sus hashes. El proceso predictor registra accesos y bloquea fuentes de 2021 generales y de 2023/2025. El conjunto nacional completo de PASO 2021 no está permitido en el predictor.

El marco se reconstruye de los campos de claves/electores del archivo oficial: esos campos describen información que podía conocerse antes del escrutinio, aunque no se dispone de una copia fechada ex ante de ese padrón. La disponibilidad de un acta (algún voto cargado) se trata como metadato de recepción, no como voto a un partido. Se selecciona entre actas disponibles, con criterios independientes de sus resultados, y se informa la cobertura de ese universo. No se sustituyen actas según el resultado.

## Modelos y desarrollo temporal

- Fuerzas fijadas por nombres sin umbral de votos: JXC, FDT (continuidad peronista/kirchnerista declarada en el mapeo), FIT, LIB y OTRAS. No se seleccionan fuerzas por sus totales finales. El mapeo de nombres se conserva, con reservas para alianzas cambiantes.
- Orígenes de PASO 2021: diputados generales 2019 y 2017, promedio de votos proyectados sobre un marco común. Todo antecedente es anterior al destino. No se usa noviembre de 2021.
- Modelo congelado: Goodman lambda=0,1, AMBA/resto y factor de banda 1,4. Se etiqueta como configuración retrospectiva, pues sus constantes se eligieron mirando años posteriores.
- Variante temporal: elegir lambda entre 0,01; 0,1; 1 y swing (infinito) por menor MAE medio por fuerza en diputados 2017, usando diputados 2013 y 2015 como orígenes. Empates: mayor regularización. Calibrar el factor de las bandas del margen con diputados 2019, usando 2015 y 2017 como orígenes y la lambda ya elegida. Factor mínimo 1; cuantil 95 % de la expansión necesaria, redondeado hacia arriba a décimas. No recalibrar después de evaluar 2021.
- Baselines: porcentaje crudo, porcentaje postestratificado AMBA/resto y swing uniforme. Ablaciones: un solo origen 2019, sin repesado y sin regularización; las constantes se fijan antes del resultado. Se medirán sobre las mismas actas. ICG, gobernadores, Zipf y ajustes de bancas quedan fuera del experimento PASO.

## Muestras

100 colecciones por diseño, cada una con 30 mesas únicas. Semilla base 12092021, separada por diseño/repetición/año. Diseños: azar uniforme; reparto por distrito proporcional a electores (restos mayores); 10 circuitos con 3 mesas por circuito; Twitter con 20 AMBA/10 resto y racimos; Twitter parcial (mismas mesas, terceros ocultos en las primeras 10); geográfico por circuitos pequeños; estrés partidario usando únicamente el perfil FDT del origen histórico. La parcialidad oculta LIB/FIT/OTRAS; conserva JXC y FDT por identificación predeclarada, no por ranking del resultado destino. La selección sesgada no puede mirar el voto de 2021.

Bootstrap de circuitos: 200 remuestras por muestra para modelos principales. Desarrollo histórico: 30 colecciones por diseño, 100 remuestras para calibración de 2019; lambda se elige con puntos de 2017. No se presentan las repeticiones como elecciones independientes.

## Evaluación fijada

MAE por fuerza, MAE del margen JXC-FDT firmado, error por distrito, ganadores distritales, cobertura y ancho de bandas 95 % nacionales y del margen, frecuencia de primer puesto contra todas las fuerzas y Brier diagnóstico. Comparaciones emparejadas sobre idénticas actas; resultados por diseño y elección, sin ocultar fallos. Brier de una sola elección y muestras dependientes no prueba calibración de probabilidades entre elecciones. Se examina la sensibilidad a lambda y componentes, sin elegir el ganador después de ver PASO 2021. No se exige un umbral de éxito inventado a posteriori: se informa si supera los baselines y si la cobertura observada es compatible con su nivel nominal, con incertidumbre y dependencia explícitas.

Las correcciones por errores técnicos posteriores al sellado deberán registrarse como enmiendas y obligarán a distinguir corridas invalidadas de válidas. No se cambiarán parámetros por ver errores del destino. La prueba prospectiva futura sigue pendiente: se congelará una nueva versión antes de la próxima elección y se guardarán predicciones antes del cierre.
