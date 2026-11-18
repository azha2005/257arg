"""Importa las estimaciones IDW ya preparadas por los atlas, por código censal."""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
ATLAS25 = ROOT / "mapas/mapaAMBA2025radios"
SERIE = ROOT / "mapas/serieAMBA2005_2023radios"
SOURCES = [
    ("25", "Diputados 2025", ATLAS25 / "asignacion_idw.pkl", "Locales de octubre de 2025"),
    ("23", "Presidencial 2023", SERIE / "asignacion_2023pres.pkl", "Locales de 2025 como referencia"),
    ("23b", "Balotaje 2023", SERIE / "asignacion_2023bal.pkl", "Locales de 2025 como referencia"),
]


def read_script(path, receiver):
    content = path.read_text(encoding="utf-8").strip()
    prefix = receiver + "("
    if not content.startswith(prefix) or not content.endswith(");"):
        raise ValueError(f"Formato inesperado en {path}")
    return json.loads(content[len(prefix):-2])


def preparar_locales(data_path, write_js):
    candidates25 = json.loads((ATLAS25 / "dataset_amba2025radios.json").read_text(
        encoding="utf-8"))["candidates"]
    loaded = []
    for key, label, filename, method in SOURCES:
        source = pd.read_pickle(filename)
        positions = [i for i, name in enumerate(source["CATS"]) if not name.startswith("_")]
        parties = [source["CATS"][i] for i in positions]
        candidates = {code: candidates25["P_" + code] for code in parties} if key == "25" else source["candidates"]
        votes = source["A"][:, positions]
        expected = 8_179_068 if key == "25" else source["ctrl"]["positivos_asignados"]
        if not math.isclose(votes.sum(), expected, rel_tol=0, abs_tol=1e-5):
            raise ValueError(f"{filename.name}: totales distintos a los del atlas")
        ids = source["radios"].COD_2022.astype(str)
        if not ids.is_unique or not np.isfinite(votes).all() or (votes < 0).any():
            raise ValueError(f"{filename.name}: votos o códigos inválidos")
        loaded.append((key, label, method, candidates, pd.DataFrame(votes, columns=parties, index=ids)))

    reference = set(loaded[0][-1].index)
    if any(set(votes.index) != reference for *_, votes in loaded) or len(reference) != 18_101:
        raise ValueError("Los tres atlas no cubren los mismos radios del AMBA")

    from pba import ampliar
    loaded = ampliar(loaded, data_path.parent)
    reference = set(loaded[0][-1].index)
    coverage = {}
    for district, indec in (("01", "02"), ("02", "06")):
        base = read_script(data_path / f"{district}-radios.js", "recibirBase")
        ids = sorted(code for code in reference if code.startswith(indec))
        units = {row[0]: row[2] for row in base["unidades"]}
        if not set(ids) <= units.keys():
            raise ValueError(f"{district}: hay radios de los atlas sin polígono en el editor")
        definitions, arrays = [], []
        offset = 0
        for key, label, method, candidates, votes in loaded:
            slice_ = votes.loc[ids]
            parties = [name for name, total in slice_.sum().items() if total > 0]
            definitions.append({
                "id": key, "nombre": label, "desde": offset, "metodo": method,
                "partidos": [candidates[code]["n"] for code in parties],
                "colores": [candidates[code]["base"] for code in parties],
            })
            arrays.append(slice_[parties].to_numpy())
            offset += len(parties)
        rows = {key: row for key, row in zip(ids, np.concatenate(arrays, axis=1).tolist())}
        write_js(data_path / f"{district}-locales.js", "recibirLocales", {
            "id": district, "elecciones": definitions, "votos": rows
        })
        coverage[district] = len(rows)
        print(f"{district}: {len(rows):,} de {len(units):,} radios con estimación de los atlas", flush=True)

    catalog = read_script(data_path / "catalogo.js", "recibirCatalogo")
    for item in catalog:
        item["geolocalizados"] = coverage.get(item["id"], 0)
    write_js(data_path / "catalogo.js", "recibirCatalogo", catalog)
