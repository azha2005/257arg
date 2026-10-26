"""Codigo de columna de la base de Ernesto -> grupo de la tabla de Wikipedia (Elecciones legislativas de 1993)."""
FAM = {
 "PJ": "fjufe pj fje fes afjupo fpv fup fj fjr frejupo fjpsc fjv fcr",         # Total Partido Justicialista y aliados: 7.112.922
 "UCR": "ucr ucrp afcs",                                                       # 4.946.281
 "MOD": "mod",                                                                 # 946.310
 "FG": "fg jpc fgds atc fcor aap anfg fp mjs pi pc",                           # Total Frente Grande: 634.720
 "UCD": "ucd aopl",                                                            # 435.093
 "US": "ahte aus asm ausdc psp fcps psa fupro",                                # Total Unidad Socialista: 408.517
 "PO": "fit mst po fut",                                                       # Total Partido Obrero y aliados: 124.093
 "FR": "fr", "PDP": "pdp", "PAL": "paldpdc", "ACHA": "acha", "PRS": "ren", "PD": "pd", "MAS": "mas", "MPN": "mpn", "PF": "fed", "MPJ": "mpj",
 "MCI": "mci", "BLO": "blo", "MPP": "mpatp", "BJU": "bju", "MID": "mid", "PTP": "ptp", "CI": "ci", "MPF": "mpf", "CR": "cr", "PH": "ph", "NC": "nc", "DC": "dc",
}
SKIP = {"fjpsc01", "fjpsc02"}   # sublistas de Santa Cruz que repiten votos del FJPSC: no suman a los positivos de la unidad
CODE2BLOC = {c: b for b, cs in FAM.items() for c in cs.split()}
