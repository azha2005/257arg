"""Qué atlas van al sitio de GitHub Pages y cómo se agrupan (2-nov-2026).

Cada entrada: (ruta del HTML desde la raíz, año, rótulo, nota corta o "").
Lo que no está acá no se publica (wiki.html, hemiciclos, mapa2007circuitos, que era una prueba, ni el AMBA 2007 por circuito).
"""

GRUPOS = [
    ("1904", "Circunscripciones uninominales, 1904", "Las 120 circunscripciones de la ley 4161; votos publicados por candidato y afiliación partidaria.", [
        ("mapas/mapa1904/atlas_1904.html", "1904", "Diputados nacionales", "59 de 60 circunscripciones con votos"),
    ]),
    ("1912-1930", "Ley Sáenz Peña, 1912 a 1930", "Por departamento, con Cantón, actas del Congreso y prensa de época.", [
        ("mapas/mapa1912/atlas_1912_diputados.html", "1912", "Diputados nacionales", "Cobertura parcial"),
        ("mapas/mapa1914/atlas_1914_diputados.html", "1914", "Diputados nacionales", "Cobertura parcial"),
        ("mapas/mapa1916dip/atlas_1916_diputados.html", "1916", "Diputados nacionales", ""),
        ("mapas/mapa1922/atlas_1922.html", "1922", "Presidente", ""),
        ("mapas/mapa1928/atlas_1928.html", "1928", "Presidente", ""),
        ("mapas/mapa1930/atlas_1930.html", "1930", "Diputados nacionales", ""),
    ]),
    ("1946-1973", "Peronismo y proscripción, 1946 a 1973", "Cantón y la base de Lupu y Stokes.", [
        ("mapas/mapa1946/atlas_1946.html", "1946", "Presidente", ""),
        ("mapas/mapa1948/atlas_1948.html", "1948", "Diputados nacionales", ""),
        ("mapas/mapa1948c/atlas_1948c.html", "1948", "Convencionales constituyentes", ""),
        ("mapas/mapa1951/atlas_1951.html", "1951", "Diputados y delegados por circunscripción", "SVG adaptado al SHP histórico"),
        ("mapas/mapa1954/atlas_1954.html", "1954", "Diputados nacionales", ""),
        ("mapas/mapa1958/atlas_1958.html", "1958", "Presidente", ""),
        ("mapas/mapa1962/atlas_1962.html", "1962", "Diputados nacionales", ""),
        ("mapas/mapa1965/atlas_1965.html", "1965", "Diputados nacionales", ""),
        ("mapas/mapa1973/atlas_1973.html", "1973", "Presidente, marzo", ""),
        ("mapas/mapa1973s/atlas_1973s.html", "1973", "Presidente, septiembre", ""),
    ]),
    ("1983-2001", "Democracia, 1983 a 2001", "Base de Ernesto Calvo, cotejada con las tablas de la Wikipedia.", [
        ("mapas/mapa1983/atlas_1983.html", "1983", "Presidente", ""),
        ("mapas/mapa1983dip/atlas_1983_diputados.html", "1983", "Diputados nacionales", ""),
        ("mapas/mapa1985/atlas_1985.html", "1985", "Diputados nacionales", ""),
        ("mapas/mapa1987/atlas_1987.html", "1987", "Diputados nacionales", ""),
        ("mapas/mapa1989/atlas_1989.html", "1989", "Presidente", ""),
        ("mapas/mapa1989dip/atlas_1989_diputados.html", "1989", "Diputados nacionales", ""),
        ("mapas/mapa1991/atlas_1991.html", "1991", "Diputados nacionales", ""),
        ("mapas/mapa1993/atlas_1993.html", "1993", "Diputados nacionales", ""),
        ("mapas/mapa1994/atlas_1994.html", "1994", "Convencionales constituyentes", ""),
        ("mapas/mapa1995/atlas_1995.html", "1995", "Presidente", ""),
        ("mapas/mapa1995dip/atlas_1995_diputados.html", "1995", "Diputados nacionales", ""),
        ("mapas/mapa1997/atlas_1997.html", "1997", "Diputados nacionales", ""),
        ("mapas/mapa1999/atlas_1999.html", "1999", "Presidente", ""),
        ("mapas/mapa1999dip/atlas_1999_diputados.html", "1999", "Diputados nacionales", ""),
        ("mapas/mapa2001/atlas_2001.html", "2001", "Diputados nacionales", ""),
        ("mapas/mapa2001bronca/atlas_2001bronca.html", "2001", "Diputados, con el voto bronca", "Blancos y nulos como una opción"),
    ]),
    ("pres2003-2023", "Presidente, 2003 a 2023", "Primeras vueltas y balotajes por departamento. Votos locales de PolAr y la DINE; cartel nacional de la Wikipedia.", [
        ("mapas/mapa2003pres/atlas_2003pres.html", "2003", "Presidente", ""),
        ("mapas/mapa2007pres/atlas_2007pres.html", "2007", "Presidente", ""),
        ("mapas/mapa2011pres/atlas_2011pres.html", "2011", "Presidente", ""),
        ("mapas/mapa2015pres/atlas_2015pres.html", "2015", "Presidente, primera vuelta", ""),
        ("mapas/mapa2015bal/atlas_2015bal.html", "2015", "Presidente, balotaje", ""),
        ("mapas/mapa2019pres/atlas_2019pres.html", "2019", "Presidente", ""),
        ("mapas/mapa2023pres/atlas_2023pres.html", "2023", "Presidente, primera vuelta", ""),
        ("mapas/mapa2023bal/atlas_2023bal.html", "2023", "Presidente, balotaje", ""),
    ]),
    ("2003-2025", "Diputados nacionales, 2003 a 2025", "Escrutinio por mesa de la DINE y PolAr, agrupado como la Wikipedia.", [
        ("mapas/mapa2003/atlas_2003.html", "2003", "Diputados nacionales", ""),
        ("mapas/mapa2005/atlas_2005.html", "2005", "Diputados nacionales", ""),
        ("mapas/mapa2007/atlas_2007.html", "2007", "Diputados nacionales", ""),
        ("mapas/mapa2009/atlas_2009.html", "2009", "Diputados nacionales", ""),
        ("mapas/mapa2011/atlas_2011.html", "2011", "Diputados nacionales", ""),
        ("mapas/mapa2013/atlas_2013.html", "2013", "Diputados nacionales", ""),
        ("mapas/mapa2015/atlas_2015.html", "2015", "Diputados nacionales", ""),
        ("mapas/mapa2017/atlas_2017.html", "2017", "Diputados nacionales", ""),
        ("mapas/mapa2019/atlas_2019.html", "2019", "Diputados nacionales", ""),
        ("mapas/mapa2021/atlas_2021.html", "2021", "Diputados nacionales", ""),
        ("mapas/mapa2023/atlas_2023.html", "2023", "Diputados nacionales", ""),
        ("mapas/mapa2025/atlas_2025.html", "2025", "Diputados nacionales", ""),
    ]),
    ("paso", "PASO, 2011 a 2023", "Gana la agrupación; la ficha de cada unidad muestra las listas internas.", [
        ("mapas/mapa2011paso/atlas_2011paso.html", "2011", "PASO presidente", ""),
        ("mapas/mapa2011pasodip/atlas_2011pasodip.html", "2011", "PASO diputados", ""),
        ("mapas/mapa2013paso/atlas_2013paso.html", "2013", "PASO diputados", ""),
        ("mapas/mapa2015paso/atlas_2015paso.html", "2015", "PASO presidente", ""),
        ("mapas/mapa2015pasodip/atlas_2015pasodip.html", "2015", "PASO diputados", ""),
        ("mapas/mapa2017paso/atlas_2017paso.html", "2017", "PASO diputados", ""),
        ("mapas/mapa2019paso/atlas_2019paso.html", "2019", "PASO presidente", ""),
        ("mapas/mapa2019pasodip/atlas_2019pasodip.html", "2019", "PASO diputados", ""),
        ("mapas/mapa2021paso/atlas_2021paso.html", "2021", "PASO diputados", ""),
        ("mapas/mapa2023paso/atlas_2023paso.html", "2023", "PASO presidente", ""),
        ("mapas/mapa2023pasodip/atlas_2023pasodip.html", "2023", "PASO diputados", ""),
    ]),
    ("amba", "AMBA por circuito y por radio censal", "Capital y 40 partidos. Por radio son estimaciones: el voto se publica por mesa.", [
        ("mapas/mapaAMBA2003radios/atlas_amba2003radios.html", "2003", "Presidente, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2005dip.html", "2005", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2007dip.html", "2007", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2007pres.html", "2007", "Presidente, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2009dip.html", "2009", "Diputados, por radio", "Estimado; 321 radios excluidos"),
        ("mapas/serieAMBA2005_2023radios/atlas_2011dip.html", "2011", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2011pres.html", "2011", "Presidente, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2013dip.html", "2013", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2015dip.html", "2015", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2015pres.html", "2015", "Presidente, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2015bal.html", "2015", "Balotaje, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2017dip.html", "2017", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2019dip.html", "2019", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2019pres.html", "2019", "Presidente, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2021dip.html", "2021", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2023pasofuerza.html", "2023", "PASO presidente, por radio", "Estimado; por fuerza"),
        ("mapas/serieAMBA2005_2023radios/atlas_2023pasocand.html", "2023", "PASO presidente, por radio", "Estimado; por precandidato"),
        ("mapas/serieAMBA2005_2023radios/atlas_2023pasointernas.html", "2023", "Internas de la PASO, por radio", "Estimado; seis internas"),
        ("mapas/serieAMBA2005_2023radios/atlas_2023dip.html", "2023", "Diputados, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2023pres.html", "2023", "Presidente, por radio", "Estimado"),
        ("mapas/serieAMBA2005_2023radios/atlas_2023bal.html", "2023", "Balotaje, por radio", "Estimado"),
        ("mapas/mapaAMBA2025radios/atlas_amba2025radios.html", "2025", "Diputados, por radio", "Estimado"),
    ]),
    ("escenarios", "Escenarios hipotéticos", "Ucronías y simulaciones a partir de resultados reales. No son resultados.", [
        ("mapas/mapa1916fic/atlas_1916_alt.html", "1916", "Presidente, ucronía", "De la Torre contra el ex-PAN"),
        ("mapas/mapa1983hipotetico/atlas_1983_hipotetico.html", "1983", "Presidente", "Luder 50,33 %"),
        ("mapas/mapa1985hip/atlas_1985hip.html", "1985", "Presidente", ""),
        ("mapas/mapa1985peronismo/atlas_1985_peronismo.html", "1985", "Diputados", "Peronismo unido"),
        ("mapas/mapa1989convergencia/atlas_1989_convergencia.html", "1989", "Presidente", "Casella y Convergencia"),
        ("mapas/mapa1995/atlas_1995_ucr_frepaso.html", "1995", "Presidente", "FREPASO y UCR sumados"),
        ("mapas/mapa2003escenarios/index.html", "2003", "Presidente, 18 retiradas", "Un atlas por candidato que se baja"),
        ("mapas/mapa2003alt/index.html", "2003", "Ocho escenarios alternativos", "Originales de u/Alarmed_Rope5383"),
        ("mapas/mapa2023massa/atlas_2023massa.html", "2023", "Presidente", "Massa 40,21 %"),
        ("mapas/mapa2027/atlas_2027.html", "2027", "Presidente y balotaje", "Simulación"),
        ("mapas/mapa2027kic/atlas_2027kic.html", "2027", "Balotaje", "Kicillof contra Milei"),
    ]),
]

# Además de las entradas, se publican estos HTML (atlas enlazados desde otra página del sitio).
EXTRA = ["mapas/mapa2003escenarios/atlas_2003_sin_*.html",
         "mapas/mapa2003alt/atlas_2003alt_*.html",
         "mapas/mapaAMBA2003radios/atlas_amba2003radios_pob.html",
         "mapas/mapaAMBA2025radios/atlas_amba2025radios_pob.html"]

# Páginas que no son atlas (simulador y sankeys enlazados): se copian tal cual, sin la capa del sitio.
CRUDOS = ["analisis/escenarios2003/simulador_2003.html",
          "transferencias/1999pe_2003pe/sankey_1999pe_2003pe.html",
          "transferencias/2003p_2005/sankey_2003p_2005.html",
          "transferencias/2003p_2007p/sankey_2003p_2007p.html",
          "transferencias/2003p_2009/sankey_2003p_2009.html"]

# Miniatura de las entradas que no son un atlas.
MINI = {"mapas/mapa2003escenarios/index.html": "mapas/mapa2003escenarios/atlas_2003_sin_k.html"}
MINI["mapas/mapa2003alt/index.html"] = "mapas/mapa2003alt/atlas_2003alt_bilardo.html"
CRUDOS += ["mapas/mapa2003alt/LEEME_2003ALT.md"]
CRUDOS += [f"mapas/mapa2003alt/estimacion_{c}.csv" for c in
           ("macri", "alvarez", "bilardo", "kirchner", "rodriguezsaa", "lemas", "menem", "reutemann")]
CRUDOS += [f"mapas/mapa2003alt/miniaturas/{c}{suffix}.webp" for c in
           ("macri", "alvarez", "bilardo", "kirchner", "rodriguezsaa", "lemas", "menem", "reutemann") for suffix in ("", "_oscuro")]
CRUDOS += ["mapas/mapa2003alt/miniaturas/portada.jpg", "mapas/mapa2003alt/assets/Epilogue-OFL.txt"]
CRUDOS += [f"mapas/mapa2003alt/assets/epilogue-{weight}.woff2" for weight in (400,600,700)]
