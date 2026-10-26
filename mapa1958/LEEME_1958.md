# Atlas 1958

Elección presidencial del 23 de febrero de 1958. Construido con `python canton5865/atlas5865.py 1958` (constructor compartido de 1958, 1962 y 1965).

**Datos**: Cantón (1968), t. II, transcripto y corregido. La revisión, las correcciones y las anomalías están en
[`canton5865/LEEME.md`](../canton5865/LEEME.md). Resultado nacional (torta, barras y métricas): tabla de la Wikipedia (`wikitop.py`, `WIKI[1958]`).
Porcentajes sobre votos positivos.

**Bloques** (solo los que ganan alguna unidad): UCRI (Frondizi), UCRP (Balbín), conservadores (PD, Conservador, Unión Provincial, PD Conservador, PD Formoseño, PD Liberal: las filas que la Wikipedia enlaza al PDN/FNPC), UCRI Rojo y Blanco y Partido Populista.

**Casos particulares**: Corrientes (Cantón solo trae diputados) y Río Negro (no está en Cantón): color sólido con el total provincial de la Wikipedia. Tierra del Fuego: Cantón suma sus votos a Capital.

**Geometría**: `Departamentos_1960_2026v2` + las 20 secciones electorales de Capital (`Departamentos_1960_secc CF`). Partidos y departamentos con datos que el mapa de 1960 no tiene llevan polígono propio, nunca se fusionan (pedido del usuario): Misiones con sus once departamentos anteriores a 1960 (mapa de 1947; la asignación de Frontera → General Manuel Belgrano y de San Pedro no está verificada). Polígonos sin fila en Cantón (partidos que todavía no existían, como Escobar o Tres de Febrero en 1958) quedan beige y rotulados. Malvinas en gris; Tierra del Fuego y la Antártida en gris (territorio nacional).

**Colores**: UCRP rojo #e10019 (el de la UCR en todos los atlas). UCRI salmón anaranjado #f4845f (pedido del usuario: salmón como la Wikipedia, #E36552, pero corrido hacia el naranja para que no se confunda con el rojo de la UCRP en los tonos oscuros). Conservadores/FNPC azul marino #1f2f6b (el de la Wikipedia para la FNPC en la tabla de 1962, y el del PD en 1983). UCRI Rojo y Blanco frambuesa #c2185b; Partido Populista (Catamarca) celeste #35aae0.

**Logos** (infobox de la Wikipedia; ver `logos_wikipedia/LICENCIAS.md`): escudo de la UCRI de 1963, escudo de la UCRP (redibujo de 2024), bandera justicialista con el escudo clásico (1946) para el peronismo y los neoperonistas, logo de la FNPC (digitalización de 2025), Unión Popular (redibujo de 2019), MID (1963), PSD (redibujo de 2018), escudo del PDP y estrella bloquista. Sin logo, con sigla: conservadores (PD), UCRI Rojo y Blanco (RyB) y Partido Populista (PP).

**Modos**: GANÓ, UCRI, UCRP, PART. En participación, gris claro = sin padrón o con más votantes que inscriptos en la fuente.

**Salidas**: `atlas_1958.html`, `dataset_1958.json`, `img/`, `png_transparentes/mapa1958/`, `png_blanco/mapa1958/`. Sin paquete de Commons todavía.
