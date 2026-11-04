# Verificación de cierre, 28-oct-2026

- `test_correcciones.py`: 11 pruebas, todas pasan.
- Compilación Python de los motores, CLI, simulador de Congreso, aguja, dibujo e ICG: sin errores.
- `informe.py`: emparejamiento uno a uno de las 1.000 muestras por versión; 30 actas retenidas en todas las corridas corregidas. La anterior conserva 30 en 942, 29 en 55 y 28 en 3. Las muestras de entrada tienen 30 mesas únicas.
- Ejecutados los backtests guardados, la comparación de las actas reales y la regeneración operativa de su Markdown, HTML y evolución temporal.
- Gráfico comparativo y evolución temporal revisados como imágenes. Corregida la superposición de la leyenda del comparativo y el rótulo de frecuencias de primer puesto en la aguja.
- La captura del HTML mediante Edge no pudo verificarse: el proceso de prueba falló con acceso denegado al arrancar y mostró un diálogo de error. El HTML quedó generado, pero no se afirma inspección visual de su render en este cierre. La instancia de prueba (PID 2600) ya no estaba activa en la comprobación posterior; no se cerraron sesiones ajenas.
- No se modificaron las transcripciones originales. `baseline/` conserva el código previo y las salidas reales anteriores.

Los resultados son retrospectivos y condicionales a estos diseños de muestra. Las limitaciones de cobertura y bancas están detalladas en `RESULTADOS.md`.
