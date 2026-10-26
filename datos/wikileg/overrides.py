# (anio, camara) -> {nombre de la lista en la DINE: fragmento del nombre del bloque de Wikipedia}; None = dejar sin agrupar
OVR = {
    (2011, "DIPUTADOS"): {
        "Coalición Cívica - Afirmación para una República Igualitaria ARI": "Coalición Cívica",
        "Alianza Coalición Cívica - Afirmación para una República Igualitaria ARI": "Coalición Cívica",
        "Alianza Frente Justicialista para la Victoria": "Frente para la Victoria",
        "Pro-Propuesta Republicana": "Frente Popular-Propuesta",
        "GEN": "Frente Amplio Progresista",
        "Partido Autonomista": "Partido Autonomista de la Capital",
    },
    (2013, "DIPUTADOS"): {"UNEN": "Progresista Cívico", "ALIANZA FRENTE AMPLIO PROGRESISTA": "Progresista Cívico", "UNION PD-PRO": "Propuesta Republicana",
                          "MOVIMIENTO SOCIALISTA DE LOS TRABAJADORES (MST)": "Nueva Izquierda"},
    (2015, "DIPUTADOS"): {"PROPUESTA FREPAM": "Cambiemos"},
    (2017, "DIPUTADOS"): {"FRENTE JUSTICIALISTA": "peronismo no kirchnerista", "FRENTE DE LA VICTORIA": "Unidad Ciudadana", "FRENTE UNIDAD Y RENOVACION": "peronismo no kirchnerista",
                          "FRENTE RENOVADOR 1PAIS": "1Pa", "DEL OBRERO": "Frente de Izquierda", "OBRERO": "Frente de Izquierda"},
    (2011, "SENADORES"): {"Alianza Frente Popular": "Frente Popular-Propuesta", "Coalición Cívica - Afirmación para una República Igualitaria ARI": "Coalición Cívica",
                          "Alianza Coalición Cívica - Afirmación para una República Igualitaria ARI": "Coalición Cívica", "Alianza Frente Justicialista para la Victoria": "Frente para la Victoria",
                          "Pro-Propuesta Republicana": "Frente Popular-Propuesta"},
    (2013, "SENADORES"): {"UNEN": "Progresista Cívico", "ALIANZA FRENTE AMPLIO PROGRESISTA": "Progresista Cívico", "FRENTE POPULAR": "Frente Renovador"},
    (2015, "SENADORES"): {"PROPUESTA FREPAM": "Cambiemos"},
    (2017, "SENADORES"): {"FRENTE DE LA VICTORIA": "Unidad Ciudadana", "FRENTE JUSTICIALISTA": "peronismo no kirchnerista", "FRENTE UNIDAD JUSTICIALISTA SAN LUIS": "peronismo no kirchnerista"},
}


# 2005-2009 (PolAr_Data): correcciones por (provincia, nombre de la lista en PolAr) -> fragmento del nombre del grupo de Wikipedia (None = sin grupo)
OVRP = {
    (2009, "DIPUTADOS"): {
        ("Ciudad de Buenos Aires", "ENC. POP. P/ VICTORIA - FTE P/ LA VICTORIA"): "kirchnerismo",
        ("Buenos Aires", "PTS - MAS - IZQUIERDA SOCIALISTA"): "Frente de Izquierda y de los Trabajadores",
        ("San Luis", "FTE. JUSTICIALISTA ES POSIBLE"): "Peronismo Federal",
        ("La Rioja", "FTE. JUSTICIALISTA DEL PUEBLO"): "kirchnerismo",
        ("Ciudad de Buenos Aires", "AL. DIALOGO POR LA CIUDAD"): "Diálogo",
        ("Buenos Aires", "MST-MIJD-NUEVA IZQUIERDA EN UNIDAD"): "Movimiento Socialista de los Trabajadores-Nueva",
        ("Mendoza", "COMPROMISO POPULAR"): "kirchnerismo",
        ("Mendoza", "AL. POLO SOLIDARIO HUMANISTA"): "kirchnerismo",
        ("Chubut", "AL.FTE CIVICO POPULAR"): None,
        ("Entre Ríos", "AL. FTE. POPULAR DISIDENTE"): None,
    },
    (2009, "SENADORES"): {
        ("Córdoba", "AL. UNION POR CORDOBA - COMPROMISO FEDERAL"): "Peronismo Federal",
        ("Corrientes", "ENC. CORRIENTES - ACUERDO CIVICO Y SOCIAL"): "Encuentro por Corrientes",
        ("Corrientes", "FTE. CORRENTINOS POR EL CAMBIO (+ columna repetida 0543 en la fuente)"): "Correntinos por el Cambio",
    },
    (2007, "DIPUTADOS"): {
        ("Santa Fe", "Partido Socialista"): "Coalición Cívica",
        ("Mendoza", "Coalición ARI - Partido Socialista"): "Coalición Cívica",
        ("Córdoba", "Frente Grande"): "Córdoba Nueva",
        ("Mendoza", "FREJUVI"): "Frente para la Victoria",
        ("Mendoza", "Concertación Plural"): "Frente para la Victoria",
        ("Buenos Aires", "Alianza Frente PTS-MAS Izquierda Socialista"): "Frente de Izquierda",
        ("Córdoba", "Alianza Frente PTS-MAS Izquierda Socialista"): "Frente de Izquierda",
    },
    (2005, "DIPUTADOS"): {("Buenos Aires", "Alianza MAS-PTS"): "Movimiento al Socialismo"},
    (2005, "SENADORES"): {("Buenos Aires", "Alianza MAS-PTS"): "Movimiento al Socialismo", ("Buenos Aires", "Alianza Encuentro Amplio"): "Encuentro Amplio"},
}
