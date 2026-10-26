# Formato de `dataset.json`

Un solo archivo describe todo lo que cambia entre un atlas y otro. `build_atlas.py --dataset dataset.json` lo incrusta en el HTML y el JS de la plantilla dibuja a partir de él; no hay nada de una elección concreta en el código.

```jsonc
{
  "slug": "elecciones_1976",                       // prefijo de los archivos descargados (opcional)
  "locale": "es-AR",                               // formato de números: 1.234 / 12,34 (opcional)
  "country": "Argentina",                          // título del panel de detalle cuando no hay nada seleccionado
  "title": "Elecciones presidenciales de Argentina de",
  "year": "1976",                                  // va en la caja con los colores de la bandera
  "labels": {"results":"Resultados","won":"GANÓ",  // textos fijos (opcional; estos son los valores por defecto)
             "pie1":"Proporción de votos por candidato",
             "pie2":"Anillo exterior: Participación","provinces":"Provincias"},
  "exterior": {"caption":"sin voto en 1976",       // bajo el globo "Exterior"; omitir caption si hubo voto exterior
               "color":"#7d7f82", "label":"Exterior"},
  "bins": [40,50,60,70,80,90],                     // umbrales (en %) entre los 7 tonos; por defecto los de 1999
  "bin_labels": ["30%","40%","50%","60%","70%","80%","+90%"],
  "sets": {"1":{"label":"1ª V."},                  // agrupa modos en "juegos" de pestañas (opcional)
           "2":{"label":"2ª V.","subtitle":"Segunda vuelta · simulación"}},

  "candidates": {                                  // el código es libre ("UCR", "A", "Lista 3"…)
    "UCR": {"n":"Alfonsín / Alende",               // nombre en la leyenda
            "sub":"FREDEPO",                       // segunda línea (partido/frente); opcional
            "logo":"UCR",                          // sigla grande a la izquierda de la barra
            "base":"#dc0143",                      // color del tono "1" (el de 40–50 %); de él salen los 7 tonos
            "bar":"#dc0143",                       // fondo de la barra de la leyenda (por defecto = base)
            "txt":"#c99600",                       // color del % si la barra es clara u oscura (por defecto = bar)
            "minor":true}                          // true = candidatura menor/blanco/nulo: sale en la tarjeta, en la mini ventana y en el CSV
  },

  "modes": [                                       // cada modo = una pestaña = un mapa completo
    {
      "id": "dept",                                // se elige con  #m-dept  en la URL o --start-mode
      "tile": "DEPT",                              // texto de la pestaña (máx. 4 por set, ~5 letras)
      "set": "1",                                  // a qué set pertenece (por defecto "1")
      "note": "texto de la barra superior",        // aclaración metodológica; fuera del poster
      "units": [ /* 538 entradas, una por territorio, en el orden de assets/territories.json */
        {"w":"UCR", "q":36.74,                     // ganador y su % → tono por tramo
         "lines":[["UCR",25584,36.74],["PJ",23344,33.5]],   // [código, votos, %] para el tooltip (votos o % pueden ser null)
         "metrics":[["Votos válidos","69.632"],["Participación (votos)","70.896"]],   // cifras grandes del panel (opcional)
         "sections":[{"title":"Correspondencia con los tres mapas históricos",
                      "rows":[["marzo 1973","Azul 72 % · rojo 23 %"]]}],               // bloques de la columna derecha del panel (opcional)
         "note":"Estimación"},                     // nota gris (tooltip y panel)
        {"fill":"#3b7bbf", "lines":[["X",null,71.2]]}        // alternativa: color explícito (coropletas, márgenes, participación…)
      ],
      "prov": {"Buenos Aires":{"w":"UCR","q":36.36, "lines":[…], "metrics":[…], "sections":[…]}, … },   // las 24 provincias, mismo formato que units (o {"fill":…}); lines/metrics/sections alimentan el panel al elegir una provincia
      "national": {
        "cands":  [{"code":"UCR","votes":4236882,"pct":33.93}, …],   // filas de la leyenda, ordenadas; la 1.ª lleva "GANÓ"
        "slices": [{"code":"UCR","v":4236882},{"fill":"#717274","v":240000}],   // pie; si falta se arma con cands
        "partp":  83.02,                                              // % de participación para el anillo; null lo oculta
        "metrics":[["Votos válidos","12.5 M"]]                        // cifras del panel cuando no hay selección (opcional)
      },
      "legend": {"title":"Participación",          // opcional: leyenda propia para mapas de color explícito
                 "stops":[["#e8f1fa","60%"],["#08306b","90%"]],
                 "bars": false}                    // false = no dibujar las barras de candidatos
    }
  ]
}
```

## Reglas que conviene respetar

- **`units` en el orden de `territories.json`** (538 entradas: departamentos, partidos y las circunscripciones de CABA). El script `scripts/match_territories.py` empareja un CSV propio (provincia + departamento) con ese índice y lista lo que no encuentra. `build_atlas.py` aborta si la cantidad no coincide.
- **`prov` debe tener las 24 provincias**, con los nombres de `territories.json` (con tildes: "Córdoba", "Entre Ríos", "Tucumán", "Capital Federal"). Se usa para la mini "Provincias", para la Antártida/Islas (color de Tierra del Fuego) y para el recuadro de CABA dentro del AMBA (color de "Capital Federal").
- **Un mapa por provincia** (no por departamento) = repetir el valor provincial en todas las `units` de esa provincia; `prov` queda igual.
- **Tonos por tramo**: con `w` y `q`, el color sale de `candidates[w].base` según el tramo de `q` (`bins`). Con `fill` no hay tono ni rampa en la leyenda: usar `legend.stops`.
- **Rampas en la leyenda**: solo aparecen para los candidatos que ganan al menos un territorio en ese modo, y los tonos que nadie alcanza salen atenuados (como en 1999).
- **Participación y pie**: el pie reparte `slices` (o `cands`); el anillo oscuro cubre `partp` % del círculo desde las 12 en sentido horario.
- Los números son datos del usuario: si son estimaciones o simulaciones, decirlo en `note` y en `subtitle` del set.

## Interactividad (viene con la plantilla; se alimenta de los mismos campos)
- **Rueda / botones ±**: zoom del mapa principal (hasta 40×, las líneas mantienen su grosor); **arrastrar** = desplazar; **Restaurar** = vista completa. Los recuadros, el pie y la leyenda no se mueven, así el poster conserva su aspecto.
- **Clic en un departamento**: lo resalta (también en los recuadros) y fija una **tarjeta flotante** junto al cursor con los resultados: ganador, `metrics`, barra y porcentaje de **cada candidatura** (`lines`: todas, incluidas las menores, blanco y nulo), `sections` y `note`. Se cierra con × o Esc, y sigue al cambiar de pestaña.
- **Selector de provincia**: atenúa el resto y acerca la provincia; la tarjeta pasa a los datos de `prov[nombre]`. **Buscador** de departamento con autocompletar (“Nombre — Provincia”).
- **Pasar el mouse**: mini ventana con **los mismos resultados** que la tarjeta (sin las secciones largas). Si hay una tarjeta fija, la mini ventana se corre para no taparla.
- **Descargas**: SVG y PNG de lo que se ve (PNG transparente) y **CSV** del modo actual con votos y % de todas las candidaturas por territorio.
- El hash `#bare` (o `#bare-white`, con `-m-<id>` para el modo) oculta barra y panel: es lo que usan `shot.sh` y `cmp.ps1` para comparar con la referencia.
