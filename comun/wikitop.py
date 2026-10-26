"""Resultado nacional («topline») de cada atlas, tomado tal cual de la tabla de resultados del artículo de la Wikipedia en español.

El mapa (departamentos y provincias) sale de Cantón (1968); la torta, las barras y las métricas nacionales salen de acá, para que el
atlas diga lo mismo que el artículo donde se va a subir. Los porcentajes son sobre votos positivos (válidos), como en Wikipedia.

    import wikitop; cands, slices, partp, metrics = wikitop.national(1930)
"""

# Los códigos de bloque son los de cada build_*.py. «otros» = filas de la tabla que no forman bloque en el atlas.
WIKI = {
    1912: dict(
        art="Elecciones legislativas de Argentina de 1912",
        # el «Total» de la tabla (682.461) suma los votos del primer candidato de cada partido (lista incompleta: se votaba por varios cargos); sobre él se calculan los %
        blocs={"CON": 283745, "UCR": 121262, "UN": 82778, "UC": 60567, "SOC": 37020, "LDS": 17630},
        otros=17102 + 1643 + 60714,             # Unión Comunal, Defensa Rural, Otros
        positivos=682461, blancos=677 + 18, dif=51323, total=654631, inscriptos=935001,
        extra=[["Votos válidos (electores)", 602613]],
        lab_pos="Votos a candidatos", lab_bla="En blanco e impugnados", lab_nul="Diferencia de actas"),
    1914: dict(
        art="Elecciones legislativas de Argentina de 1914",
        blocs={"CON": 249345, "UCR": 210843, "SOC": 55014, "UC": 20222, "LDS": 16601},
        otros=2863 + 815 + 588 + 35307,         # Unión Popular, Partido Liberal, Partido Nacionalista, Otros (independientes)
        positivos=591598, blancos=5180 + 5, dif=16068, total=612851, inscriptos=1027542,
        lab_pos="Votos válidos", lab_bla="En blanco y anulados", lab_nul="Diferencia de actas"),
    1916: dict(
        art="Elecciones legislativas de Argentina de 1916",
        blocs={"UCR": 339296, "CON": 187812, "PDP": 74061, "SOC": 54838, "SAR": 34052, "RAD": 29173, "CCI": 17910},
        otros=759 + 20163,                      # Partido Unitario, Otros
        positivos=758064, blancos=3757 + 114 + 95, dif=9998, total=772028, inscriptos=1189254,
        lab_pos="Votos válidos", lab_bla="En blanco, anulados y sobres vacíos"),
    1922: dict(
        art="Elecciones presidenciales de Argentina de 1922",
        blocs={"UCR": 419170, "CON": 231102, "SOC": 78472, "DIS": 58749, "PDP": 41841},
        otros=1 + 809,                          # Unión Radical Jujeña, Otros
        positivos=830144, blancos=14462, dif=33046, total=877652, inscriptos=1586366,
        lab_pos="Votos positivos", lab_bla="En blanco"),
    1928: dict(
        art="Elecciones presidenciales de Argentina de 1928",
        blocs={"YRI": 839140, "MEL": 430050, "SOC": 67423, "PDP": 14173, "MAT": 6000},
        otros=4658 + 1286 + 493 + 2996,         # PC, PCRA, PC Obrero, Otros
        positivos=1366219, blancos=65245, dif=30141, total=1461605, inscriptos=1807566,
        lab_pos="Votos positivos", lab_bla="En blanco"),
    1930: dict(
        art="Elecciones legislativas de Argentina de 1930",
        blocs={"UCR": 622961, "CD": 296854, "RAN": 164654, "PS": 123680, "PSI": 110761, "PDP": 57996, "LEN": 19378, "BLO": 2885},
        otros=12778 + 12307 + 6863 + 2476 + 2361 + 2263 + 3204,   # Bandera Blanca, Salud Pública, PC, Agrario, PCRA, Popular, Otros
        positivos=1441421, blancos=31920, dif=11607, total=1485651, inscriptos=1983246,
        lab_pos="Votos positivos", lab_bla="En blanco y anulados"),
    1958: dict(
        art="Elecciones presidenciales de Argentina de 1958",
        # CON = filas conservadoras de la tabla (PD, Conservador, Conservador FNPC, Unión Provincial, PD Conservador, PD Formoseño, PD Liberal)
        blocs={"UCRI": 4070398, "UCRP": 2617693, "CON": 145935 + 128226 + 30239 + 10722 + 10328 + 2364 + 16611, "URB": 31987, "NPE": 7596},
        otros=8224373 - (4070398 + 2617693 + 344425 + 31987 + 7596),
        positivos=8224373, blancos=841400, dif=22724, total=9088497, inscriptos=10002327,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    1962: dict(
        art="Elecciones legislativas de Argentina de 1962",
        blocs={"FJ": 3049327, "UCRI": 2284091, "UCRP": 1793945, "FNPC": 610963, "PSD": 250172, "PDP": 156114},
        otros=8751556 - (3049327 + 2284091 + 1793945 + 610963 + 250172 + 156114),
        positivos=8751556, blancos=332956, dif=0, total=9084512, inscriptos=10596321,
        lab_pos="Votos válidos", lab_bla="En blanco y anulados"),
    1965: dict(
        art="Elecciones legislativas de Argentina de 1965",
        blocs={"UP": 2786244, "UCRP": 2660937, "FNPC": 661108, "MID": 538057, "MPP": 513721, "UCRI": 404689, "PDP": 287250, "UCRB": 75225,
               "MFL": 37435, "PUN": 3273},
        otros=8954249 - (2786244 + 2660937 + 661108 + 538057 + 513721 + 404689 + 287250 + 75225 + 37435 + 3273),
        positivos=8954249, blancos=357871, dif=37708, total=9349828, inscriptos=11168564,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    1983: dict(
        art="Elecciones presidenciales de Argentina de 1983",
        # solo los bloques que ganan al menos una unidad del mapa; el resto (PI, MID, Alianza Federal, UCD, ...) va en «otros»
        blocs={"UCR": 7724559, "PJ": 5995402, "PAL": 104052, "BLO": 58038, "MPN": 30546, "MFP": 15298},
        otros=14927512 - (7724559 + 5995402 + 104052 + 58038 + 30546 + 15298),
        positivos=14927512, blancos=334946, dif=87728, total=15350186, inscriptos=17929951,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    1985: dict(
        art="Elecciones legislativas de Argentina de 1985",
        # solo los bloques que ganan al menos una unidad del mapa; el resto (PI, Frente del Pueblo, PF, Unidad Socialista, PDP, ...) va en «otros»
        blocs={"UCR": 6678647, "PJ": 3753194, "REN": 1611441, "UCD": 570490, "PAL": 172470, "PRS": 71134, "BLO": 50985, "MPN": 33520},
        otros=15324510 - (6678647 + 3753194 + 1611441 + 570490 + 172470 + 71134 + 50985 + 33520),
        positivos=15324510, blancos=205406, dif=96353, total=15626269, inscriptos=18653487,
        lab_pos="Votos válidos", lab_bla="En blanco", lab_nul="Anulados"),
    1987: dict(
        art="Elecciones legislativas de Argentina de 1987",
        # solo los bloques que ganan al menos una unidad del mapa; el resto (PI, Unidad Socialista, MAS, FRAL, PDP, MID, ...) va en «otros»
        blocs={"UCR": 5972588, "PJ": 6622252, "UCD": 926988, "FAP": 98249, "PAL": 166746, "MPN": 61859, "ABL": 59131, "PPR": 38150},
        otros=16037652 - (5972588 + 6622252 + 926988 + 98249 + 166746 + 61859 + 59131 + 38150),
        positivos=16037652, blancos=326959, dif=77241, total=16455932, inscriptos=19420204,
        extra=[["Diferencia de actas", 14080]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Nulos"),
    1989: dict(
        art="Elecciones presidenciales de Argentina de 1989",
        # solo las fuerzas que ganan al menos una unidad del mapa; el resto (Izquierda Unida, Jubilados, Fuerza Republicana, ...) va en «otros»
        blocs={"MEN": 7957518, "ANG": 6213217, "ALS": 1200172, "EBO": 240132, "MPN": 35466},
        otros=16749128 - (7957518 + 6213217 + 1200172 + 240132 + 35466),
        positivos=16749128, blancos=222048, dif=116049, total=17091620, inscriptos=20034252,
        extra=[["Diferencia de actas", 4395]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    1995: dict(
        art="Elecciones presidenciales de Argentina de 1995",
        # candidaturas de la tabla de Wikipedia; Rico (310.069) y los demas van en «otros»
        blocs={"MEN": 8687511, "BOR": 5096104, "MAS": 2956137},
        otros=17395284 - (8687511 + 5096104 + 2956137),
        positivos=17395284, blancos=653443, dif=125112, total=18203924, inscriptos=22178201,
        extra=[["Diferencia de actas", 30085]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    "1995u": dict(
        art="Elecciones presidenciales de Argentina de 1995",
        # version hipotetica: Bordon (FREPASO) y Massaccesi (UCR) sumados
        blocs={"MEN": 8687511, "OPO": 5096104 + 2956137},
        otros=17395284 - (8687511 + 5096104 + 2956137),
        positivos=17395284, blancos=653443, dif=125112, total=18203924, inscriptos=22178201,
        extra=[["Diferencia de actas", 30085]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    1994: dict(
        art="Elecciones de convencionales constituyentes de Argentina de 1994",
        # solo los grupos que ganan al menos una unidad del mapa; el resto (Unidad Socialista, UCeDe, PDP, Alianza por el No, ...) va en «otros»
        blocs={'UCR': 3114166, 'PJ': 6072335, 'FG': 2082622, 'MOD': 1461451, 'PD': 217631, 'PAL': 187030, 'FR': 277808, 'MPN': 47023, 'MPJ': 56813, 'PRS': 93429, 'CI': 10140},
        otros=15772343 - (3114166 + 6072335 + 2082622 + 1461451 + 217631 + 187030 + 277808 + 47023 + 56813 + 93429 + 10140),
        positivos=15772343, blancos=782477, dif=224163, total=16778983, inscriptos=21644991,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Nulos"),
    1991: dict(
        art="Elecciones legislativas de Argentina de 1991",
        # solo los grupos que ganan al menos una unidad del mapa; el resto va en «otros»
        blocs={'PJ': 6425437, 'UCR': 4539967, 'UCD': 981611, 'CFI': 490099, 'PAL': 167276, 'MPN': 80648, 'FR': 282478, 'BLO': 74603, 'CR': 77425, 'MPF': 9704, 'CI': 24089},
        otros=15728688 - (6425437 + 4539967 + 981611 + 490099 + 167276 + 80648 + 282478 + 74603 + 77425 + 9704 + 24089),
        positivos=15728688, blancos=834407, dif=127323, total=16738503, inscriptos=20817039,
        extra=[["Diferencia de actas", 48085]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Nulos"),
    1993: dict(
        art="Elecciones legislativas de Argentina de 1993",
        # solo los grupos que ganan al menos una unidad del mapa; el resto va en «otros»
        blocs={'PJ': 7112922, 'UCR': 4946281, 'PAL': 181611, 'ACHA': 125597, 'MPN': 55375, 'PRS': 120669, 'FR': 227727, 'CI': 24219},
        otros=16361265 - (7112922 + 4946281 + 181611 + 125597 + 55375 + 120669 + 227727 + 24219),
        positivos=16361265, blancos=700565, dif=180590, total=17242420, inscriptos=21463761,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    1997: dict(
        art="Elecciones legislativas de Argentina de 1997",
        # «Total» de cada fila de la tabla (Alianza = UCR + FREPASO + aliados, incluso donde fueron por separado); solo los grupos que ganan al menos una unidad
        blocs={'ALI': 8097301, 'PJ': 6274385, 'AR': 662403, 'FR': 247129, 'PD': 228291, 'PN': 223668, 'PDJ': 77476, 'MPN': 42701},
        otros=17251484 - (8097301 + 6274385 + 662403 + 247129 + 228291 + 223668 + 77476 + 42701),
        positivos=17251484, blancos=958676, dif=262219, total=18472741, inscriptos=23198858,
        extra=[["Diferencia de actas", 362]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Nulos"),
    2001: dict(
        art="Elecciones legislativas de Argentina de 2001",
        # «Total» de cada fila-grupo de la tabla; solo los grupos que ganan al menos una unidad (FUBA y AR son filas sueltas de la tabla)
        blocs={'PJ': 5499353, 'ALI': 3244891, 'ARI': 1300438, 'PAUFE': 296804, 'AR': 160832, 'FUBA': 156104, 'PD': 126769, 'MPN': 60852},
        otros=14290108 - (5499353 + 3244891 + 1300438 + 296804 + 160832 + 156104 + 126769 + 60852),
        positivos=14290108, blancos=2022587, dif=2486296, total=18798991, inscriptos=24907838,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Nulos"),
    2009: dict(
        art="Elecciones legislativas de Argentina de 2009",
        blocs={'ACyS': 5705105, 'FPV': 5544069, 'PRO': 3675747, 'PF': 1560298,
               'SUR': 448711, 'FRC': 212621, 'MPN': 78703, 'UdN': 24496, 'NE': 415961},
        otros=19326863-(5705105+5544069+3675747+1560298+448711+212621+78703+24496+415961),
        positivos=19326863, blancos=805090, dif=352549, total=20477584, inscriptos=27942194,
        extra=[["Votos impugnados", 8]],
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
    2013: dict(
        art="Elecciones legislativas de Argentina de 2013",
        # «Total de alianzas ligadas a…» y filas individuales de la tabla nacional; solo los grupos que ganan al menos una unidad
        blocs={'FPV': 7425261, 'FPCyS': 5510949, 'FR': 4087402, 'PRO': 1974049, 'FIT': 1211252,
               'UxC': 532702, 'FRC': 260034, 'CF': 259195, 'PACh': 153395, 'FE': 149169,
               'MPN': 133952, 'SST': 113404, 'PJ': 105412, 'PARES': 37649, 'MIJD': 23470},
        otros=22614402 - (7425261 + 5510949 + 4087402 + 1974049 + 1211252 + 532702 + 260034 + 259195 + 153395 + 149169 + 133952 + 113404 + 105412 + 37649 + 23470),
        positivos=22614402, blancos=846171, dif=325063, total=23785636, inscriptos=30635464,
        lab_pos="Votos positivos", lab_bla="En blanco", lab_nul="Anulados"),
}
# Claves separadas para no reemplazar los atlas presidenciales de los mismos años.
WIKI.update({
    '1983_diputados': dict(art='Elecciones legislativas de Argentina de 1983',
        blocs={'UCR':7104748,'PJ':5697610,'PAL':113482,'MFP':16490,'MPN':36168,'BLO':61737},
        otros=14811231-(7104748+5697610+113482+16490+36168+61737),positivos=14811231,
        blancos=451756,dif=87199,total=15350186,inscriptos=17929951,
        lab_pos='Votos positivos',lab_bla='En blanco',lab_nul='Anulados'),
    '1989_diputados': dict(art='Elecciones legislativas de Argentina de 1989',
        blocs={'PJ':7460488,'UCR':4865835,'ADC':1796271,'MPN':49070,'CFI':565080,'CR':87273,'FR':213957},
        otros=16645516-(7460488+4865835+1796271+49070+565080+87273+213957),positivos=16645516,
        blancos=307578,dif=99482,total=17092120,inscriptos=20034252,extra=[['Diferencia de actas',39544]],
        lab_pos='Votos positivos',lab_bla='En blanco',lab_nul='Anulados'),
    '1995_diputados': dict(art='Elecciones legislativas de Argentina de 1995',
        blocs={'PJ':8371132,'UCR':3718920,'FREP':3599764,'PAL':158269,'MPN':60781},
        otros=16953823-(8371132+3718920+3599764+158269+60781),positivos=16953823,
        blancos=1087334,dif=122995,total=18202652,inscriptos=22177954,extra=[['Diferencia de actas',38500]],
        lab_pos='Votos positivos',lab_bla='En blanco',lab_nul='Anulados'),
    '1999_diputados': dict(art='Elecciones legislativas de Argentina de 1999',
        blocs={'ALI':8497076,'PJ':7153786,'UBO':289860,'AR':1502732,'PD':235357,'MPN':89798},
        otros=18516870-(8497076+7153786+289860+1502732+235357+89798),positivos=18516870,
        blancos=1122980,dif=192862,total=19832712,inscriptos=24107414,
        lab_pos='Votos positivos',lab_bla='En blanco',lab_nul='Anulados'),
})
for y, w in WIKI.items():   # cada tabla tiene que cerrar con sus propios votos positivos
    assert sum(w["blocs"].values()) + w["otros"] == w["positivos"], y
    # (1930: positivos + blancos + diferencia de actas = 1.484.948, pero el artículo da 1.485.651 de total; se dejan las cifras tal cual)


# 1965: la tabla nacional de la Wikipedia omite Catamarca, Formosa, La Rioja y Misiones, que sí votaron diputados nacionales
# según el resumen nacional de Cantón (1968, t. I, p. 239-246, «Resultados Electorales de 1965. Ministerio del Interior»;
# solo Jujuy y Salta «no hubo elecciones»). Se suman con las cifras departamentales de Cantón (t. II, corregidas): con ellas los
# inscriptos dan 11.460.766, exactamente el total del tomo I. «UPM» es la Unión Provincial de Misiones (gana 7 departamentos).
_C65 = dict(blocs={"UCRP": 63322, "UP": 46284, "MID": 21784, "UPM": 21861, "UCRI": 9977, "MPP": 9540, "FNPC": 3403, "PDP": 1158},
            otros=30111, positivos=207440, blancos=3961, dif=616, total=212017, inscriptos=292202)
_w = WIKI[1965]
for _b, _v in _C65["blocs"].items(): _w["blocs"][_b] = _w["blocs"].get(_b, 0) + _v
for _k in ("otros", "positivos", "blancos", "dif", "total", "inscriptos"): _w[_k] += _C65[_k]
assert sum(_w["blocs"].values()) + _w["otros"] == _w["positivos"] and _w["inscriptos"] == 11460766
_w["nota"] = (" La tabla nacional de la Wikipedia omite Catamarca, Formosa, La Rioja y Misiones; se suman con las cifras de Cantón "
              "(t. I y II), que las trae como elecciones de diputados nacionales.")

def _n(v):
    return "{:,}".format(int(v)).replace(",", ".")


def _p(v):
    return ("%.2f" % v).replace(".", ",")


def national(year, other_fill="#717274"):
    """-> cands, slices (torta: bloques + otros, sobre votos positivos), partp, metrics"""
    w = WIKI[year]; pos = w["positivos"]
    cands = sorted([{"code": b, "votes": v, "pct": round(100 * v / pos, 2)} for b, v in w["blocs"].items()], key=lambda c: -c["votes"])
    slices = [{"code": c["code"], "v": c["votes"]} for c in cands] + [{"fill": other_fill, "v": w["otros"]}]
    partp = round(100 * w["total"] / w["inscriptos"], 2)
    metrics = [["Inscriptos", _n(w["inscriptos"])], ["Votantes", _n(w["total"])], ["Participación", _p(partp) + " %"],
               [w["lab_pos"], _n(pos)], [w["lab_bla"], _n(w["blancos"])]]
    if w.get("lab_nul"): metrics.append([w["lab_nul"], _n(w["dif"])])
    for lab, v in w.get("extra", []): metrics.append([lab, _n(v)])
    return cands, slices, partp, metrics


def note(year):
    return ("Resultado nacional (torta y barras): tabla de «%s» en la Wikipedia en español, porcentajes sobre votos positivos; "
            "departamentos y provincias: Cantón (1968), también sobre votos positivos." % WIKI[year]["art"] + WIKI[year].get("nota", ""))


# Diputados 2003–2025: snapshots nacionales producidos por el constructor compartido.
# Los atlas de referencia 2009/2013 conservan sus entradas y decisiones originales.
import json as _json
from pathlib import Path as _Path
for _year in (2003,2005,2007,2011,2015,2017,2019,2021,2023,2025):
    _snapshot=_Path(__file__).resolve().parent.parent/'mapas'/f'mapa{_year}'/f'wiki_nacional_{_year}.json'
    if _snapshot.exists():
        _row=_json.loads(_snapshot.read_text(encoding='utf8'))
        assert sum(_row['blocs'].values())+_row['otros']==_row['positivos'],_year
        WIKI[_year]=_row
