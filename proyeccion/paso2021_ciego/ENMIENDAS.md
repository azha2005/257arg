# Enmiendas posteriores a la apertura del destino

No se cambiaron modelos, parámetros, muestras ni predicciones. Todos los hashes de `PREDICCIONES_SELLADAS.json` deben seguir verificando.

Se corrigió únicamente la representación del evaluador: los baselines y ablaciones sin bootstrap tenían `cubre=false` e `inferencia_valida=false` por valor predeterminado. Esos campos no habían sido calculados y deben quedar ausentes (`NaN`), en lugar de aparentar una cobertura medida del 0 %. El informe solo comparaba cobertura en los modelos principales; sus cifras no cambian. El evaluador original y la tabla anterior se preservan en `enmiendas/`.

`evaluar.py` difiere por esta corrección del hash inicial del protocolo; la copia `enmiendas/evaluar_previa.py` debe coincidir con ese hash. La verificación de cierre registra ambos y comprueba igualdad exacta de las predicciones y de las métricas puntuales antes/después. Los demás scripts firmados y los parámetros conservan sus hashes originales.
