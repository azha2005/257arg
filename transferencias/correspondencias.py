"""Cruces históricos documentados. Solo sumas de territorios completos, sin repartir votos.

Fuentes, reservas y catálogos: correspondencias_2013_2017/LEEME.md.
"""
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def apply_hacia_2019(A, B, y0, y1):
    """Cambios documentados y normalización de claves para los cuatro cruces nuevos."""
    start = 2017 if y0 == 2017 else 2015
    records = []

    def transform(T, year):
        keys = []
        for d, s, c in T.index:
            target, source, reason = (d, s, c), None, None
            if d == "21" and start == 2015 and s == 6 and c in ("399", "399A", "399B", "399C"):
                target = (d, s, "G:399")
                source, reason = "sf_res543_2015", "Venado Tuerto: union del circuito anterior y sus subdivisiones"
            if d == "24" and s == 1:
                if start == 2015:
                    target = (d, s, "G:USHUAIA")
                    source, reason = "tdf_disp8_2017+tdf_res291_2017", "Ushuaia agregada: division interna de 2015 no equivalente a la de 2019"
                elif c.startswith("U") and c[1:].isdigit():
                    target = (d, s, "U" + str(int(c[1:])))
                    source, reason = "DINE_2017_2019_claves", "Normalizacion del sufijo numerico: U001 equivale a U1"
            if d == "24" and s in (2, 5) and c == "21":
                target = (d, 5, c)
                source, reason = "tdf_ley1186_2017+DINE_2019_ambitos", "Tolhuin conserva circuito 21 y pasa de seccion 2 a 5"
            if source:
                records.append(dict(anio=year, distrito=d, seccion=s, circuito=c,
                                    seccion_comun=target[1], circuito_comun=target[2], motivo=reason, fuente_id=source))
            keys.append(target)
        result = T.copy()
        result.index = pd.MultiIndex.from_tuples(keys, names=T.index.names)
        result = result.groupby(level=[0, 1, 2]).sum().sort_index()
        assert np.allclose(result.sum().values, T.sum().values, rtol=0, atol=1e-7)
        return result

    A, B = transform(A, start), transform(B, 2019)
    reserve = "Neuquen por departamento; demas claves comunes por circuito. No se reparten votos ni se completan circuitos ausentes."
    if start == 2015:
        reserve += " Ushuaia agregada y Venado Tuerto reunificado."
    else:
        reserve += " Ushuaia por circuito tras normalizar U001/U1; Tolhuin por circuito 21."
    return A, B, {"version": f"{start}_2019_v1", "registros": records, "reserva": reserve}


def apply_2015_2023(A, B, y0, y1):
    """Santa Fe según tabla CNE; subdivisiones verificadas de Cipolletti y Santa Cruz."""
    start_year = int(str(y0).rstrip('pb'))
    table = pd.read_csv(HERE / "correspondencias_2013_2017" / "santa_fe_2022.csv",
                        dtype={"circuito_anterior": str, "circuito_nuevo": str})
    old = {(r.seccion_anterior, r.circuito_anterior): (r.seccion_anterior, "SF:" + r.circuito_anterior) for r in table.itertuples()}
    new = {(r.seccion_nueva, r.circuito_nuevo): (r.seccion_anterior, "SF:" + r.circuito_anterior) for r in table.itertuples()}
    end_year = int(str(y1).rstrip('pb'))
    if end_year == 2025:
        from estimar import secnames
        section_names = {year: secnames(year) for year in (start_year, 2025)}
    records = []

    def transform(T, year):
        keys = []
        for d, s, c in T.index:
            target, source, reason = (d, s, c), None, None
            if d == "21":
                match = (old if year == start_year else new).get((s, c))
                if match:
                    target = (d, *match)
                    source, reason = "sf_res66_2022", "Recodificacion oficial CNE, anexo de equivalencias"
                else:
                    target = (d, s, f"PENDIENTE{year}:" + c)
            groups = [
                ("16", 12, "65", [str(n) for n in range(6501, 6525)], "rn_res186_2022"),
                ("20", 1, "3", ["300", "310", "320"], "sc_cne68_2022"),
                ("20", 7, "18", [str(n) for n in range(1800, 1851, 10)], "sc_res28_2024"),
            ]
            for dd, ss, parent, children, src in groups:
                if (d, s) == (dd, ss) and c in ([parent] if year == start_year else children):
                    target = (d, s, "G:" + parent)
                    source, reason = src, f"Subdivision: suma al circuito de {start_year}"
            # Tolhuin se separó entre las dos elecciones. Sin un cruce interno completo,
            # la isla es la unión territorial común; la Antártida queda separada.
            if d == "24" and s in ((1, 2) if year == start_year else (1, 2, 5)):
                target = (d, 0, "G:ISLA_GRANDE")
                source, reason = "tdf_ley1186_2017", "Union insular comun: cambios de secciones y circuitos sin equivalencia interna"
            if d == "24" and s == 3:
                target = (d, s, "G:ANTARTIDA")
                source, reason = f"DINE_{start_year}_{end_year}_ambitos", "Antartida separada: suma de bases por cambio de codificacion"
            if end_year == 2025 and ((d == '16' and s in (4, 7, 8, 9, 11)) or (d == '19' and s in (1, 3, 8)) or (d == '20' and s == 4)):
                target = (d, s, 'G:SECCION_' + str(s))
                source, reason = f'DINE_{start_year}_2025_ambitos', 'Seccion completa: nuevas subdivisiones sin equivalencia interna verificada; no se emparejan padres que perdieron territorio'
            if end_year == 2025 and d == '21':
                name = section_names[year][(d, s)]
                if name in {'LAS COLONIAS','GARAY','VERA','SAN JAVIER','ROSARIO','CASEROS','CONSTITUCION'}:
                    target = (d, 0, 'S:' + name)
                    source, reason = f'sf_res66_2022+DINE_{start_year}_2025_ambitos', 'Solo departamento con nuevas claves posteriores a la tabla calculada: union completa, sin equivalencia interna inventada'
            if source:
                records.append(dict(anio=year, distrito=d, seccion=s, circuito=c,
                                    seccion_comun=target[1], circuito_comun=target[2], motivo=reason, fuente_id=source))
            keys.append(target)
        result = T.copy()
        result.index = pd.MultiIndex.from_tuples(keys, names=T.index.names)
        result = result.groupby(level=[0, 1, 2]).sum().sort_index()
        assert np.allclose(result.sum().values, T.sum().values, rtol=0, atol=1e-7)
        return result

    A, B = transform(A, start_year), transform(B, end_year)
    return A, B, {"version": f"{start_year}_{end_year}_v1", "registros": records,
                  "reserva": "Neuquen por departamento; Tierra del Fuego como isla principal agregada y Antartida separada, sin equivalencia interna inventada." + (" Santa Fe conserva las equivalencias calculadas de CNE 66/2022; solo Las Colonias, Garay, Vera, San Javier, Rosario, Caseros y Constitucion van por departamento por claves posteriores pendientes. Secciones 4/7/8/9/11 de Rio Negro, 1/3/8 de San Luis y 4 de Santa Cruz completas por cambios internos pendientes de correspondencia." if end_year == 2025 else "")}


def common_early_key(key, origin):
    from historicos_1989 import territory
    d,s,c = key
    if not c.startswith('S:UNION_'): c = territory(d,c.removeprefix('S:'),'1989p')
    if d == '02' and c in ('S:PELLEGRINI','S:TRESLOMAS'): c = 'S:UNION_PELLEGRINI'
    if d == '10' and c in ('S:CAPITAL','S:PALPALA'): c = 'S:UNION_CAPITAL'
    if origin == '1983p' and d == '08' and c in ('S:GUALEGUAYCHU','S:ISLASDELIBICUY'): c = 'S:UNION_GUALEGUAYCHU'
    return d,s,c

def new_historical_key(key,y0,y1):
    d,s,c=key
    if (y0,y1)==('1983p','1985d') and d=='08' and c in ('S:GUALEGUAYCHU','S:ISLASDELIBICUY'): c='S:UNION_GUALEGUAYCHU'
    if y0=='1995p' and d=='08' and c in ('S:COLON','S:CONCORDIA','S:VILLAGUAY','S:SANSALVADOR'): c='S:UNION_COLON_CONCORDIA_VILLAGUAY'
    if (y0,y1)==('1995p','1999p') and d=='24' and c in ('S:USHUAIA','S:ANTARTIDA','S:SECTORANTARTICOARGENTINO'): c='S:UNION_USHUAIA'
    return d,s,c

def apply_pair(A, B, y0, y1):
    if (y0,y1) == (2017,2025):
        return apply_2015_2023(A,B,y0,y1)
    if (y0,y1) in [('1954d','1965d'),('1958d','1962d')]:
        records=[]
        groups=[({'PILAR','TIGRE','LAS CONCHAS','ESCOBAR'},'G:PILAR+TIGRE+ESCOBAR','Cacopardo, anexo Cuadro 1, PDF67/p64'),
                ({'BOLIVAR','CARLOS CASARES','CASEROS','DAIREAUX','PEHUAJO','HIPOLITO IRIGOYEN','HIPOLITO YRIGOYEN'},'G:BOLIVAR+CASARES+CASEROS+PEHUAJO','Cacopardo, anexo Cuadro 1, PDF68/p65')]
        if y0=='1958d':
            groups.append(({'NECOCHEA','GONZALEZ CHAVES','GONZALES CHAVES','TRES ARROYOS','SAN CAYETANO'},'G:NECOCHEA+CHAVES+TRESARROYOS','Cacopardo, anexo Cuadro 1, PDF67/p64'))
        def transform(T,year):
            keys=[]
            for d,s,c in T.index:
                target='S:'+c
                why='Nombre conservado en la base Cantón'
                if d=='14' and c=='MISIONES':target,why='G:PROVINCIA_MISIONES','Provincia agregada en ambos años por redivisión; se conserva la decisión previa'
                for members,common,source in groups:
                    if d=='02' and c in members:target,why=common,source
                keys.append((d,s,target))
                records.append(dict(anio=year,distrito=d,seccion=s,circuito=c,seccion_comun=s,circuito_comun=target,motivo=why,fuente_id='DTS 47_Cacopardo_1967.pdf'))
            result=T.copy();result.index=pd.MultiIndex.from_tuples(keys,names=T.index.names)
            result=result.groupby(level=[0,1,2]).sum().sort_index()
            assert np.allclose(result.sum().values,T.sum().values,rtol=0,atol=1e-7)
            return result
        A,B=transform(A,y0),transform(B,y1)
        return A,B,{'version':'cacopardo_1967_v2','registros':records,
                    'reserva':'Escobar: unión Pilar–Tigre; Hipólito Yrigoyen: unión Bolívar–Carlos Casares–Caseros–Pehuajó. En 1958–1962 San Cayetano: unión Necochea–González Chaves–Tres Arroyos. Se suman votos y padrones completos; no se reparten cifras. Ver revision_cacopardo_1967/LEEME.md.'}
    if y0=='1914d' and y1 in ('1916d','1916de'):
        from pathlib import Path
        src=pd.read_csv(Path(__file__).parent/'fuentes_1914_1916/correspondencias.csv',dtype=str)
        records=src[src.anio.isin([y0,y1])].to_dict('records')
        return A,B,{'version':'1914_1916_observadas_v1','registros':records,
                    'reserva':'Solo unidades con columnas completas; un dato compartido se cuenta una vez. Se excluyen cifras estimadas, provincias sin desglose y Concepción del Uruguay inferida. Cobertura parcial; ver fuentes_1914_1916/LEEME.md.'}
    if (y0,y1) in [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]:
        from pathlib import Path
        source=pd.read_csv(Path(__file__).parent/'historicos_1989/correspondencias.csv',dtype=str)
        originals={(r.anio,r.distrito,r.circuito_normalizado):r.circuito for r in source.itertuples()}
        records = []
        def transform(T,year):
            keys = []
            for d,s,c in T.index:
                target = new_historical_key((d,s,c),y0,y1)[2]
                keys.append((d,s,target))
                records.append(dict(anio=year,distrito=d,seccion=s,circuito=c,departamento_original=originals[(year,d,c)],seccion_comun=s,circuito_comun=target,motivo='Unidad conservada' if target==c else 'Unión territorial completa',fuente_id='CSV Ernesto; alias y atlas locales'))
            result=T.copy()
            result.index=pd.MultiIndex.from_tuples(keys,names=T.index.names)
            result=result.groupby(level=[0,1,2]).sum().sort_index()
            assert np.allclose(result.sum().values,T.sum().values,rtol=0,atol=1e-7)
            return result
        A,B=transform(A,y0),transform(B,y1)
        return A,B,{'version':'historicos_1989_raw_v2','registros':records,
                    'reserva':'Departamentos sin fusiones ajenas al par; votos desglosados, sin abstención. '+('Deseado 1995 extrapolado por autorización previa; sin otras imputaciones. ' if y0=='1995p' else 'Sin imputaciones. Buenos Aires conserva los partidos comparables individualmente. ')+'Ver historicos_1989/LEEME.md.'}
    if (y0, y1) in [('1989p', '1995p'), ('1989d', '1994c'), ('1985d', '1987d'),('1983p','1989p'),('1987d','1989p'),('1985d','1989p'),('1989p','1997d')]:
        from pathlib import Path
        records = pd.read_csv(Path(__file__).parent / 'historicos_1989/correspondencias.csv', dtype=str)
        records = records[records.anio.isin([y0, y1])].to_dict('records')
        if y1 == '1989p':
            def transform(T,year):
                keys = [common_early_key(key,y0) for key in T.index]
                for key,target in zip(T.index,keys):
                    if key != target: records.append(dict(anio=year,distrito=key[0],seccion=key[1],circuito=key[2],seccion_comun=target[1],circuito_comun=target[2],motivo='Unión común entre bases históricas',fuente_id='atlas locales; divisiones departamentales'))
                result = T.copy()
                result.index = pd.MultiIndex.from_tuples(keys,names=T.index.names)
                result = result.groupby(level=[0,1,2]).sum().sort_index()
                assert np.allclose(result.sum().values,T.sum().values,rtol=0,atol=1e-7)
                return result
            A,B = transform(A,y0),transform(B,y1)
        return A, B, {'version':'historicos_1989_v1', 'registros':records,
                      'reserva':'Departamentos y circunscripciones de Capital; votos desglosados, sin abstención. ' + ('Deseado 1995 extrapolado por pedido del usuario. ' if (y0,y1)==('1989p','1995p') else 'Sin imputaciones de votos. ') + 'Uniones completas para cambios territoriales. Ver historicos_1989/LEEME.md.'}
    if (y0 == 2017 and y1 in (2019, "2019p")) or (str(y0) in ("2015p", "2015b") and y1 == "2019p"):
        return apply_hacia_2019(A, B, y0, y1)
    if str(y0) in ("2015pp", "2015p", "2015b") and str(y1) in ("2023p", "2023b", "2025"):
        return apply_2015_2023(A, B, y0, y1)
    early_2015 = y0 in (2009, 2013) and str(y1) in ("2015p", "2015b")
    if (y0, y1) != (2013, 2017) and not early_2015:
        return A, B, {}
    end_year = 2015 if early_2015 else 2017
    records = []

    def transform(T, year):
        keys = []
        for d, s, c in T.index:
            target, reason, source = (d, s, c), None, None
            if d == "21" and year == y0 and s in (10, 14, 15):
                target = (d, 9 if s == 10 else 13, c)
                reason, source = "Fusion de secciones; conserva circuito", "sf_res66_2022"
            if d == "21" and s == 6 and c in (["399"] if year == y0 else ["399", "399A", "399B", "399C"]):
                target = (d, s, "G:399")
                reason, source = "Venado Tuerto: suma de subdivision", "sf_res543_2015"
            if d == "16":
                for section, old, children, src in [
                    (1, "1", [str(n) for n in range(101, 123)], "rn_res613_2015"),
                    (9, "41", [str(n) for n in range(4101, 4132)], "rn_disp194_2015"),
                    (12, "63", [str(n) for n in range(6301, 6316)], "rn_res92_2024+rn_habiles_2017"),
                ]:
                    if s == section and c in ([old] if year == y0 else children):
                        target = (d, s, "G:" + old)
                        reason, source = f"Subdivision: suma al circuito de {y0}", src
            if d == "19":
                # También cambian 1007 y 1009: no emparejarlos solos por conservar código.
                urban = ["1001", "1007", "1008", "1009"] if year == y0 else [
                    "1001A", "1001B", "1001C", "1007", "1008A", "1008B", "1008C", "1008D", "1008E", "1009"]
                if s == 1 and c in urban:
                    target = (d, s, "G:1001+1007+1008+1009")
                    reason, source = "Union comun por subdivisiones y cambios de limites", "sl_disp38_2015+sl_res651_2016"
                if not early_2015 and s == 3 and c in (["3001"] if year == y0 else ["3001A", "3001B"]):
                    target = (d, s, "G:3001")
                    reason, source = "Subdivision aprobada por CNE el 30-03-2017", "sl_res376_2018"
            if not early_2015 and d == "24" and s == 1:
                target = (d, s, "G:USHUAIA")
                reason, source = "Ushuaia agregada: sin equivalencia interna verificada", "tdf_disp8_2017+tdf_res291_2017"
            if reason:
                records.append(dict(anio=year, distrito=d, seccion=s, circuito=c,
                                    seccion_comun=target[1], circuito_comun=target[2],
                                    motivo=reason, fuente_id=source))
            keys.append(target)
        result = T.copy()
        result.index = pd.MultiIndex.from_tuples(keys, names=T.index.names)
        result = result.groupby(level=[0, 1, 2]).sum().sort_index()
        assert np.allclose(result.sum().values, T.sum().values, rtol=0, atol=1e-7)
        return result

    A, B = transform(A, y0), transform(B, end_year)
    return A, B, {"version": f"{y0}_{end_year}_v1", "registros": records,
                  "reserva": "Solo sumas de circuitos completos; no se inventan equivalencias internas. Ver LEEME de correspondencias y controles del par."}
