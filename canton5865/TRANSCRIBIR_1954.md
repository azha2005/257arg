# Transcripción de Cantón 1954 (diputados, por departamento)

Fuente: Cantón, *Materiales…* (1968), t. II, `raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf`, **PDF pp. 171–248**. La página del libro es la del PDF + 7.

Cada distrito trae tres tablas: varones, mujeres y «varones y mujeres». **Solo hace falta la de varones y mujeres.** En los territorios nacionales no se votó diputados sino vicepresidente (en Santa Cruz, delegados). Esas se transcriben igual, con la elección que dice el encabezado.

## Páginas de «varones y mujeres» (ubicadas con el OCR; confirmar al abrir)
| Distrito | Elección | Varones | Mujeres | **Total** |
|---|---|---|---|---|
| Capital Federal | Diputados | 172 | 173 | **174** |
| Buenos Aires | Diputados | 175–178 | 179–182 | **183–186** |
| Catamarca | Diputados | 187 | 188 | **189** |
| Córdoba | Diputados | 190 | 191 | **192** |
| Corrientes | Diputados | 193 | 194 | **195** |
| Chaco | Diputados | 196 | 197 | **198** |
| Chubut | Vicepresidente | 199 | 200 | **201** |
| Entre Ríos | Diputados | 202 | 203 | **204** |
| Formosa | Vicepresidente | 205 | 206 | **207** |
| Jujuy | Diputados | 208 | 209 | **210** |
| La Pampa | Diputados | 211 | 212 | **213** |
| La Rioja | Diputados | 214 | 215 | **216** |
| Mendoza | Diputados | 217 | 218 | **219** |
| Misiones | Vicepresidente | 220 | 221 | **222** |
| Neuquén | Vicepresidente | 223 | 224 | **225** |
| Río Negro | Vicepresidente | 226 | 227 | **228** |
| Salta | Diputados | 229 | 230 | **231** |
| San Juan | Diputados | 232 | 233 | **234** |
| San Luis | Diputados | 235 | ? | **?** |
| Santa Cruz | Delegados | 236 | 237 | **238** |
| Santa Fe | Diputados | 239 | 240 | **241** |
| Santiago del Estero | Diputados | 242 | 243 | **244** |
| Tucumán | Diputados | 245 | ? | **?** |
| Comodoro Rivadavia (zona militar) | Vicepresidente | 246 | 247 | **248** |

En **San Luis (235)** y **Tucumán (245)** el OCR solo muestra la tabla de varones. Puede que el total esté en la misma página o que falte en el libro. Si falta, transcribí varones y mujeres por separado, que el cargador los suma.

## Formato (igual que 1958)
Un archivo por página PDF: `scratch/transcripcion/p_<página PDF>.json`. `cargar.py` lo lee sin cambios.

```json
{
  "pagina_pdf": 189,
  "pagina_libro": 196,
  "anio": 1954,
  "eleccion": "Diputados",
  "provincia": "Catamarca",
  "categoria": "varones y mujeres",
  "es_continuacion": false,
  "columnas": {"1": "Inscriptos", "2": "Votantes", "3": "Peronista", "4": "Unión Cívica Radical", "5": "Comunista", "6": "Blancos y nulos"},
  "filas": [
    {"departamento": "Ambato", "valores": {"1": 1941, "2": 1212, "3": 416, "4": 2, "5": 0, "6": 0}}
  ]
}
```
- `columnas`: en el orden de la tabla, con el nombre tal cual figura en el libro («Partido Peronista», «Unión Cívica Radical», «Partido Demócrata», «Blanco y nulos», etc.).
- `eleccion`: «Diputados», «Vicepresidente» o «Delegados», según el encabezado. El cargador usa «presid» para separar presidente de diputados: los territorios quedan como `P` y las provincias como `D`. El análisis de transferencias toma las dos.
- En las continuaciones (Buenos Aires ocupa cuatro páginas), `es_continuacion: true` y los mismos números de columna. Si en la continuación cambian los partidos, se numeran a partir del último.
- Las celdas ilegibles van como `null`. No hay que estimarlas: `sospechas.py` y `correcciones.py` se encargan después.
- Si una fila es el total de la provincia, se transcribe igual con `"departamento": "Total"`. Sirve para controlar, y el cargador la ignora en el mapa.

## Después de transcribir
1. `python canton5865/sospechas.py` (revisa que las filas sumen: votantes = partidos + blanco).
2. Avisame y armo `transferencias/1954_1958/`, la matriz de votantes 1954 → 1958 con «No votó» en las dos puntas:
   - 1954: Peronista, UCR, otros, blanco, no votó.
   - 1958: UCRI, UCRP, otros, blanco, no votó.
   - Corrientes y Río Negro no están en 1958 por departamento; Santa Cruz sí.
