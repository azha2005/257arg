# Diputados en los escenarios de 1983 y 1985

Proyección condicional del 1-nov-2026. Ejecutar `python analisis/congreso_1983_1985/calcular.py` desde la raíz. Produce `resultado.json` con detalle por provincia y `bancas.csv` con los totales.

## Resultado

| Fuerza | Cámara 1983 | Electos 1985 | Continúan de 1983, ilustrativo | Cámara 1985, ilustrativa |
|---|---:|---:|---:|---:|
| UCR | 108 | 78 | 55 | 133 |
| PJ/peronismo unido | 141 | 38 | 71 | 109 |
| Otras fuerzas | 5 | 11 | 1 | 12 |
| Total | 254 | 127 | 127 | 254 |

Mayoría absoluta: 128 de 254. Los 5 restantes de 1983 son PAL 2, Bloquista 1, MPN 1 y PI 1. Las 11 bancas nuevas de otras fuerzas en 1985 son PI 4, ADC 2, PAL-FDP 2, PDP 1, MPN 1 y PRS 1. Se mantienen sus listas distritales separadas; no se suman fuerzas distintas para aplicar D'Hondt, salvo la unión peronista expresamente solicitada y los códigos radicales aliados.

## Supuestos decisivos

1. **1983:** el mapa solicitado era presidencial. Para poder proyectar Diputados, se asume voto de lista idéntico a sus resultados simulados por provincia. No se conserva el corte de boleta legislativo histórico. No es la única proyección posible. Se usa la distribución efectiva del mapa, no una proporcionalidad nacional de 254 bancas.
2. **1985:** se usan los votos de `mapas/mapa1985peronismo/`, con FREJULI/PJ y renovadores unidos y 8,6 puntos nacionales transferidos proporcionalmente a UCR.
3. D'Hondt por provincia y Capital, con las magnitudes históricas de 1983 y de la renovación de 1985, y umbral del 3 % del padrón distrital. Magnitudes y padrones se extraen de las copias locales de las tablas provinciales de Wikipedia, 24 distritos para cada año. Los padrones oficiales tabulados evitan usar los padrones locales inconsistentes de algunas unidades de la base.
4. **Continuidad en 1985:** el sorteo histórico de mandatos de 1983 no determina el de una Cámara contrafáctica. Se ilustra un reparto equilibrado: cada fuerza conserva en cada distrito el piso o techo de la mitad de sus bancas, respetando las cantidades distritales que continuaban. Entre opciones, se asignan los sobrantes según votos de 1983. No es una reconstrucción del sorteo ni una predicción de legisladores individuales. No modela escisiones ni cambios de bloque.
5. Dentro de ese supuesto de reparto equilibrado, UCR puede terminar con 132–134 y PJ con 107–110 bancas en 1985; no son intervalos estadísticos ni límites para cualquier sorteo imaginable. Los extremos por fuerza no necesariamente se alcanzan simultáneamente. El punto ilustrativo 133/109/12 es compatible y suma 254.
6. Los pequeños desajustes de las bases de los atlas frente a sus tablas nacionales se conservan. No se corrigen votos provinciales para forzar otro reparto. Esto es una proyección sobre esas bases, no un cómputo electoral definitivo.

## Senado

No se deduce de estos dos mapas. En ese período las provincias elegían senadores mediante las legislaturas provinciales, y Capital mediante colegio electoral; Tierra del Fuego aún era territorio nacional. Simularlo requiere hipótesis adicionales sobre esas elecciones y sus renovaciones. No se asignan senadores aplicando la regla contemporánea de dos para la mayoría y uno para la minoría.

## Fuentes y controles

- [Ley 22.838, artículos 4 y 5](https://www.argentina.gob.ar/normativa/nacional/ley-22838-151849/texto): umbral de padrón y D'Hondt.
- [Elecciones legislativas de 1983](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1983) y [1985](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1985): magnitudes y padrones provinciales; copias locales `mapas/mapa1983dip/w1983.txt` y `mapas/mapa1985/w1985.txt`.
- [HCDN, Informe especial 103](https://www2.hcdn.gob.ar/export/hcdn/secparl/dgral_info_parlamentaria/dip/archivos/IE_103_Composicion_HCDN.pdf): mandatos históricos y composición por bienios, que no se trasladan mecánicamente al escenario.
- [Historia electoral argentina, edición alojada por el Ministerio de Economía](https://cdi.mecon.gob.ar/bases/docelec/az2453.pdf): renovación parcial de 1985 y elección indirecta del Senado.

Controles automáticos: 254 cargos en 1983, 127 en 1985, todos los distritos completos, 24 padrones por año, continuidad de 127 cargos y Cámara ilustrativa de 254. Comparación orientativa con los atlas históricos: reproduce las 65 bancas radicales de 1985 y las 111 justicialistas de 1983; el cómputo con la base legislativa histórica de 1983 produce 128 UCR frente a las 129 tabuladas históricamente, y 3 PAL frente a 2. Esa discrepancia adicional de fuente/listas no se fuerza a cerrar ni se presenta como validación exacta de la base. La proyección principal utiliza el mapa presidencial hipotético de 1983 bajo el supuesto explícito de voto de lista idéntico.
