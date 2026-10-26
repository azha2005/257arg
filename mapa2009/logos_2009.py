# Logos del artículo de 2009 y de sus fuerzas provinciales.
# Metadatos consultados en logos_metadata.json; reservas de época en LICENCIAS.md.
for code, filename in {
    'ACyS':'Acuerdo_Cívico_y_Socia.png',
    'FPV':'Logo_Frente_para_la_Victoria.svg',
    'PRO':'Union_Pro.png',
    'PF':'Flag_of_the_Justicialist_Party_(square_version).svg',
    'SUR':'Proyectosur_logo.png',
    'NE':'Nuevo_Encuentro_(small).png',
    'FRC':'Frente_Renovador_de_la_Concordia_Social.png',
    'MPN':'Logo_MPN.png',
    'UdN':'Logo_Frente_Grande.png',
}.items():
    CAND[code].update(_logo(filename))
