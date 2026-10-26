"""Codigo de columna de la base de Ernesto -> grupo de la tabla de Wikipedia (Elecciones legislativas de 1991)."""
FAM = {
 "PJ": "fjufe frejupo pj fjpe aufs fje fes frjun ren ajus afvj fj aun amap afec mpli afjv",       # Total Partido Justicialista y aliados: 6.425.437
 "UCR": "ucr ucrmop afcs",                                                                     # 4.539.967
 "UCD": "ucd aach aup",                                                                        # 981.611
 "US": "aus usdp ahte fjs fredejuso afp vep amp alco frp psp fps act pi fsp fdf fpgs afpcor cpop apc",   # Total Unidad Socialista y aliados: 885.057
 "MOD": "mod",                                                                                 # 543.375
 "CFI": "prs fi cfifed mpj fed",                                                               # Total CFI: 490.099
 "IU": "mas pc uti iuxs lib apu",                                                              # Total Izquierda Unida: 341.864
 "FR": "fr frf",                                                                               # 282.478
 "PAL": "paldp", "APL": "apl", "PDP": "pdp", "PD": "pd", "MPN": "mpn", "MPF": "mpf", "CI": "ci", "MPF": "mpf", "CI": "ci", "CR": "cr", "BLO": "ablo", "PO": "po",
 "DC": "dc dcug", "PTP": "ptp fvp", "NC": "nc ftp",
}
CODE2BLOC = {c: b for b, cs in FAM.items() for c in cs.split()}
SKIP = set()
