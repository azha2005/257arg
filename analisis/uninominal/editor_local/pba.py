"""Extiende a la PBA los repartos IDW de los atlas de AMBA."""

from collections import defaultdict
import json
from pathlib import Path
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely


ROOT = Path(__file__).resolve().parents[3]
ATLAS = ROOT / "mapas/mapaAMBA2025radios"
SERIE = ROOT / "mapas/serieAMBA2005_2023radios"
SURFACE = ROOT / "mapas/superficiePBA2025/locales_superficie.csv"
DINE25 = ROOT / "datos_oficiales/2025/x"
sys.path.insert(0, str(ATLAS))
sys.path.insert(0, str(SERIE))
import escuelas
import serie


def partido(name):
    normalized = escuelas.muni(name)
    return {"CORONELDEMARINALROSALES": "CORONELDEMARINALEONARDOROSALES",
            "NUEVEDEJULIO": "9DEJULIO", "VEINTICINCODEMAYO": "25DEMAYO"}.get(normalized, normalized)


def reparto(votes, seats, radios, municipalities):
    keys = [municipalities[sec] for _, sec, _ in votes.index]
    radio_keys = list(radios.county)
    ukey = lambda key: municipalities[key[1]]
    assert set(seats) == set(votes.index)
    matrix, error, _ = serie.allocate(
        votes, radios, radios.geometry.tolist(), radio_keys, ukey, seats, {}
    )
    estimated = pd.DataFrame(matrix, index=radios.pid, columns=votes.columns)
    by_county = estimated.groupby(estimated.index.str[:5]).sum()
    expected = votes.groupby(keys).sum()
    error = max(error, float((by_county - expected).abs().max().max()))
    assert error < 1e-6, error
    return estimated, error


def election_2025(surface, rolls, radios, municipalities, original):
    fields = ["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre",
              "agrupacion_nombre", "votos_tipo", "votos_cantidad"]
    parts = []
    for chunk in pd.read_csv(DINE25 / "resultados2025.csv", usecols=fields,
                             dtype={"circuito_id": str}, chunksize=750_000):
        parts.append(chunk[(chunk.distrito_id == 2) & (chunk.cargo_nombre == "DIPUTADO NACIONAL")])
    ballots = pd.concat(parts, ignore_index=True)
    ballots["sec"] = ballots.seccion_id.map("{:03d}".format)
    ballots["mesa"] = ballots.mesa_id.map("{:05d}".format)
    ballots = ballots.merge(rolls[["sec", "mesa", "lk"]], how="left", on=["sec", "mesa"], validate="many_to_one")
    assert ballots.lk.notna().all(), ballots.loc[ballots.lk.isna(), "mesa"].unique()
    aliases = dict(zip(original["LAB"].values(), original["LAB"]))
    aliases["ALIANZA FUERZA PATRIA"] = "FP"
    aliases["ALIANZA PROVINCIAS UNIDAS"] = "PU"
    positive = ballots.votos_tipo == "POSITIVO"
    ballots["cat"] = np.where(positive, ballots.agrupacion_nombre.map(aliases), "_OTROS")
    assert ballots.cat.notna().all(), ballots.loc[ballots.cat.isna(), "agrupacion_nombre"].unique()
    assert int(ballots.loc[positive, "votos_cantidad"].sum()) == int(surface.oct_pos.sum())
    local_totals = ballots.loc[positive].groupby("lk").votos_cantidad.sum()
    assert (local_totals == surface.oct_pos.reindex(local_totals.index)).all()
    ballots["unit"] = ballots.lk + "|" + ballots.circuito_id
    ballots = ballots[ballots.sec.isin(municipalities)]
    votes = ballots.pivot_table(index=["sec", "unit"], columns="cat", values="votos_cantidad",
                                 aggfunc="sum", fill_value=0)
    votes = votes[votes.sum(axis=1) > 0]
    votes["_ELOK"] = 0
    votes.index = pd.MultiIndex.from_tuples([("02", sec, unit) for sec, unit in votes.index])
    seats = {}
    for key in votes.index:
        loc = surface.loc[key[2].split("|")[0]]
        assert np.isfinite([loc.lon, loc.lat]).all(), key
        seats[key] = [(loc.lon, loc.lat, 1)]
    assigned, error = reparto(votes, seats, radios, municipalities)
    return assigned, votes, error


def centros_2023(votes, surface, municipalities):
    # Igual que la serie AMBA: incluir locales con punto comprobado en el
    # circuito de 2023 y ponderarlos por sus electores de octubre de 2025.
    sections = serie.section_names(2023)
    by_circuit = defaultdict(list)
    for feature in serie.circuitos(2023):
        p = feature["properties"]
        if p["codigo_distrito"] != "02":
            continue
        by_circuit[serie.cir(p["codigo_circuito"])].append(feature)
    geometry = {}
    for k in votes.index:
        _, sec, circ = k
        hits = by_circuit.get(circ) or by_circuit.get(circ.rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), [])
        valid = []
        for feature in hits:
            p = feature["properties"]
            if p["sistema_codigos"] == "usuario" or not p.get("nombre_seccion"):
                ok = str(p["codigo_seccion_fuente"]).zfill(3) == sec
            else:
                ok = partido(p["nombre_seccion"]) == partido(sections["02", sec])
            if ok:
                valid.append(shapely.make_valid(shapely.geometry.shape(feature["geometry"])))
        if valid:
            geometry[k] = shapely.union_all(valid)
    keys = list(geometry)
    tree = shapely.STRtree(list(geometry.values()))
    seats = defaultdict(list)
    known = surface[~surface.fuente.str.startswith("centro_") & (surface.electores > 0)]
    for local in known[known.sec.isin(municipalities)].itertuples():
        matches = tree.query(shapely.Point(local.lon, local.lat), predicate="intersects")
        for index in matches:
            key = keys[index]
            if key[1] == local.sec:
                seats[key].append((local.lon, local.lat, local.electores))
    fallback = defaultdict(list)
    for key in votes.index:
        _, sec, circ = key
        if key in seats:
            continue
        if key not in geometry:
            same = known[(known.sec == sec) & (known.cir.map(serie.cir) == circ)]
            if len(same):
                seats[key] = list(same[["lon", "lat", "electores"]].itertuples(index=False, name=None))
                fallback["locales_del_mismo_codigo_2025"].append(key)
                continue
            mapped = surface[surface.sec == sec]
            same = mapped[mapped.cir.map(serie.cir) == circ]
            if len(same):
                seats[key] = [(r.lon, r.lat, max(r.electores, 1)) for r in same.itertuples()]
                fallback["punto_de_referencia_del_mismo_codigo_2025"].append(key)
                continue
            fallback["sin_punto"].append(key)
            continue
        point = geometry[key].representative_point()
        seats[key] = [(point.x, point.y, 1)]
        fallback["centro_circuito_2023"].append(key)
    return seats, fallback


def election_2023(key, surface, radios, municipalities):
    votes, _ = pd.read_pickle(ROOT / f"transferencias/circ_2023{'p' if key == '23' else 'b'}.pkl")
    votes = votes[votes.distrito_id == "02"].copy()
    votes["sec"] = votes.seccion_id.astype(int).map("{:03d}".format)
    votes = votes[votes.sec.isin(municipalities)]
    _, aliases, _ = serie.candidates("2023pres")
    parties = {name: next(code for alias, code in aliases.items() if alias in serie.norm(name))
               for name in votes.loc[votes.votos_tipo == "POSITIVO", "agrupacion_id"].unique()}
    votes["cat"] = np.where(votes.votos_tipo == "POSITIVO", votes.agrupacion_id.map(parties), "_OTROS")
    votes["cir"] = votes.circuito.map(serie.cir)
    votes = votes.pivot_table(index=["distrito_id", "sec", "cir"], columns="cat", values="v",
                              aggfunc="sum", fill_value=0)
    votes = votes[votes.sum(axis=1) > 0]
    votes["_ELOK"] = 0
    seats, fallback = centros_2023(votes, surface, municipalities)
    if fallback["sin_punto"]:
        raise ValueError(f"{key}: falta ubicar estos circuitos: {fallback['sin_punto']}")
    assigned, error = reparto(votes, seats, radios, municipalities)
    party_cols = [c for c in votes if not c.startswith("_")]
    details = {s: {"circuitos": len(k), "positivos": int(votes.loc[k, party_cols].sum().sum())}
               for s, k in fallback.items() if k}
    return assigned, votes, error, details


def ampliar(loaded, output):
    radios = gpd.read_file(ROOT / "analisis/uninominal/shp_radios/02_buenos_aires.shp",
                           columns=["pid", "county"])
    sections = serie.section_names(2023)
    dep = json.loads((ATLAS / "depto_pba_georef.json").read_text(encoding="utf-8"))
    by_name = {partido(row["nombre"]): row["id"] for row in dep["departamentos"]}
    surface = pd.read_csv(SURFACE, dtype={"sec": str, "cir": str}).set_index("lk")
    names = surface[surface.oct_pos > 0].drop_duplicates("sec").set_index("sec").partido
    municipalities = {sec: by_name[partido(name)] for sec, name in names.items()}
    assert len(municipalities) == 135 and set(municipalities.values()) == set(radios.county)
    assert all(partido(sections["02", sec]) == partido(name) for sec, name in names.items())
    rolls = pd.read_csv(DINE25 / "localesDeVotacionyMesas.csv", dtype=str)
    rolls = rolls[rolls.distrito_id == "02"].rename(columns={"seccion_id": "sec", "mesa_id": "mesa"}).copy()
    rolls["lk"] = "02_" + rolls.sec + "_" + rolls.localvotacion_codigo
    surface["electores"] = rolls.assign(electores=rolls.mesa_electores.astype(int)).groupby("lk").electores.sum()
    outside = radios[~radios.pid.isin(loaded[0][-1].index)].reset_index(drop=True)
    extra = {sec: code for sec, code in municipalities.items() if code in set(outside.county)}
    assert len(extra) == 95 and len(outside) == 9620
    assert set(radios[~radios.pid.isin(outside.pid)].county).isdisjoint(outside.county)
    quality = surface[surface.oct_pos > 0].groupby("fuente").oct_pos.agg(["size", "sum"])
    audit = {"partidos": len(municipalities), "radios": len(radios), "partidos_ampliados": len(extra),
             "fuentes_locales_2025": {k: {"locales": int(row["size"]), "positivos": int(row["sum"])}
                                      for k, row in quality.iterrows()}, "elecciones": {}}
    result = []
    for key, label, method, candidates, amba in loaded:
        if key == "25":
            assigned, votes, error = election_2025(
                surface, rolls, outside, extra, pd.read_pickle(ATLAS / "asignacion_idw.pkl"))
            details = {}
        else:
            assigned, votes, error, details = election_2023(key, surface, outside, extra)
        parties = [c for c in votes if not c.startswith("_")]
        assert set(parties) <= set(amba.columns)
        combined = pd.concat([amba, assigned[parties]]).fillna(0)
        total = int(votes[parties].sum().sum())
        assert combined.index.is_unique and set(radios.pid) <= set(combined.index)
        assert abs(combined.sum().sum() - amba.sum().sum() - total) < 1e-6
        audit["elecciones"][key] = {"positivos_pba": round(combined.loc[radios.pid].sum().sum()),
                                    "positivos_ampliacion": total, "error_max": error, **details}
        result.append((key, label, method, candidates, combined))
        print(key, audit["elecciones"][key], flush=True)
    (output / "control_pba.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return result
