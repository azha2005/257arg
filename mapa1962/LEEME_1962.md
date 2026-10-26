# Atlas 1962

Diputados nacionales, 18 de marzo de 1962. Construido con `python canton5865/atlas5865.py 1962` (constructor compartido de 1958, 1962 y 1965).

**Datos**: Cantón (1968), t. II, transcripto y corregido. La revisión, las correcciones y las anomalías están en
[`canton5865/LEEME.md`](../canton5865/LEEME.md). Resultado nacional (torta, barras y métricas): tabla de la Wikipedia (`wikitop.py`, `WIKI[1962]`).
Porcentajes sobre votos positivos.

**Bloques** (solo los que ganan alguna unidad): Frente Justicialista (Unión Popular y las 16 listas neoperonistas que la Wikipedia suma al frente), UCRI, UCRP (con el Movimiento Radical Popular y la UCRI Lista Verde del Chaco), FNPC (conservadores, liberales y autonomistas de Corrientes, PD de Río Negro), PSD y PDP.

**Casos particulares**: Sin elección de diputados (gris): Catamarca, Formosa, La Rioja, Misiones, San Luis y Santa Cruz. Santiago del Estero eligió pero Cantón no la trae: color sólido con la tabla de la Wikipedia. Florencio Varela: columnas imputadas (página cortada; ver `canton5865/LEEME.md`).

**Geometría**: `Departamentos_1960_2026v2` + las 20 secciones electorales de Capital (`Departamentos_1960_secc CF`). Partidos y departamentos con datos que el mapa de 1960 no tiene llevan polígono propio, nunca se fusionan (pedido del usuario): Berazategui y Capitán Sarmiento (mapa de 1970, recortados a Quilmes y Bartolomé Mitre). Polígonos sin fila en Cantón (partidos que todavía no existían, como Escobar o Tres de Febrero en 1958) quedan beige y rotulados. Malvinas en gris; Tierra del Fuego y la Antártida en gris (territorio nacional).

**Colores**: UCRP rojo #e10019 (el de la UCR en todos los atlas). UCRI salmón anaranjado #f4845f (pedido del usuario: salmón como la Wikipedia, #E36552, pero corrido hacia el naranja para que no se confunda con el rojo de la UCRP en los tonos oscuros). Conservadores/FNPC azul marino #1f2f6b (el de la Wikipedia para la FNPC en la tabla de 1962, y el del PD en 1983). Frente Justicialista #318ce7 (Wikipedia). PSD ámbar #ffad00 (el del PSD en 1983; el coral #ff7f50 de 1985 en adelante se confundiría con la UCRI salmón). PDP azul #005c9e, el de todos los otros atlas (pedido del usuario).

**Logos** (infobox de la Wikipedia; ver `logos_wikipedia/LICENCIAS.md`): escudo de la UCRI de 1963, escudo de la UCRP (redibujo de 2024), bandera justicialista con el escudo clásico (1946) para el peronismo y los neoperonistas, logo de la FNPC (digitalización de 2025), Unión Popular (redibujo de 2019), MID (1963), PSD (redibujo de 2018), escudo del PDP y estrella bloquista. Sin logo, con sigla: ninguno.

**Modos**: GANÓ, FJ, UCRI, UCRP, PART. En participación, gris claro = sin padrón o con más votantes que inscriptos en la fuente.

**Salidas**: `atlas_1962.html`, `dataset_1962.json`, `img/`, `png_transparentes/mapa1962/`, `png_blanco/mapa1962/`. Sin paquete de Commons todavía.
