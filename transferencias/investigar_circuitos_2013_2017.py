"""Extrae los identificadores y nombres originales de los circuitos DINE."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "transferencias" / "correspondencias_2013_2017"


def catalogo(year):
    source = next((ROOT / "datos_oficiales" / str(year) / "x").rglob("Resultado*.csv"))
    cols = ["distrito_id", "seccion_id", "seccion_nombre", "circuito_id", "circuito_nombre", "cargo_nombre"]
    parts = []
    for chunk in pd.read_csv(source, usecols=cols, dtype=str, chunksize=1_000_000):
        sel = chunk.distrito_id.astype(int).isin([16, 19, 21, 24]) & chunk.cargo_nombre.str.upper().str.contains("DIPUTAD.*NACIONAL", na=False)
        parts.append(chunk.loc[sel, cols[:-1]].drop_duplicates())
    catalog = pd.concat(parts).drop_duplicates()
    catalog["distrito_id"] = catalog.distrito_id.astype(int).map("{:02d}".format)
    catalog["seccion_id"] = catalog.seccion_id.astype(int)
    catalog["circuito"] = catalog.circuito_id.str.strip().str.upper().str.lstrip("0").replace("", "0")
    _, elect = pd.read_pickle(ROOT / "transferencias" / f"circ_{year}.pkl")
    catalog = catalog.merge(elect.rename("electores").reset_index(), on=["distrito_id", "seccion_id", "circuito"], how="left")
    catalog = catalog.sort_values(["distrito_id", "seccion_id", "circuito"])
    catalog.to_csv(OUT / f"catalogo_{year}.csv", index=False, encoding="utf-8-sig")
    print(year, len(catalog), "filas", flush=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for year in [2013, 2017]:
        catalogo(year)
