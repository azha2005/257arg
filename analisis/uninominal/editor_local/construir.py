"""Prepara el editor sin conexión a partir del paquete QGIS (Python de Mosaic)."""

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import geopandas as gpd
import numpy as np
import shapely

from locales import preparar_locales


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "outputs/redistritacion_argentina/argentina_uninominal_qgis.zip"
OUTPUT = ROOT / "outputs/editor_uninominal"
BASE = {"D23": "Unión por la Patria", "R23": "LLA + Juntos por el Cambio",
        "D23b": "Sergio Massa", "R23b": "Javier Milei"}
GEOMETRY = {"radios": "radios_2022", "circuitos": "circuitos_2025"}
ARTIFACTS = ["index.html", "estilo.css", "app.js", "mapa.js", "plan.js", "lean.js", "LEEME.md"]
FONT_FILES = [f"epilogue-{weight}.woff2" for weight in (400, 600, 700)] + ["Epilogue-OFL.txt"]


def write_js(path, receiver, payload):
    content = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    path.write_text(f"{receiver}({content});\n", encoding="utf-8")


def write_palette(path):
    source = ROOT / "mapas/mapa2025/dataset_2025.json"
    candidates = json.loads(source.read_text(encoding="utf-8"))["candidates"]
    colors = {
        "25": {party["n"]: party["base"] for party in candidates.values()},
        "23": {"Unión por la Patria": "#009ce4", "La Libertad Avanza": "#6c4c98",
               "Juntos por el Cambio": "#fcbc00", "Hacemos por Nuestro País": "#283084",
               "Frente de Izquierda": "#e3242b", "LLA + Juntos por el Cambio": "#6c4c98"},
        "23b": {"Sergio Massa": "#009ce4", "Javier Milei": "#6c4c98"},
    }
    write_js(path, "recibirColores", colors)


def elections(frame, labels):
    deputy = [name for name in frame if name.startswith("v25_")]
    first = [name for name in frame if name.startswith("v23_")] or ["D23", "R23"]
    groups = [("25", "Diputados 2025", deputy),
              ("23", "Presidencial 2023" if first[0].startswith("v") else "Presidencial 2023 (bloques)", first),
              ("23b", "Balotaje 2023", ["D23b", "R23b"])]
    fields = []
    spec = []
    for key, title, columns in groups:
        names = [BASE[field] if field in BASE else labels[field].split(" · ", 1)[-1] for field in columns]
        spec.append({"id": key, "nombre": title, "desde": len(fields), "partidos": names})
        fields.extend(columns)
    return fields, spec


def neighbors(geometries):
    """Pares con segmento de borde compartido. Los puentes de Mosaic quedan fuera."""
    arr = geometries.array
    first, second = shapely.STRtree(arr).query(arr, predicate="intersects")
    keep = first < second
    first, second = first[keep], second[keep]
    boundary = shapely.boundary(arr)
    shared = shapely.length(shapely.intersection(boundary[first], boundary[second]))
    keep = shared > 1e-8
    return np.column_stack((first[keep], second[keep])).reshape(-1).tolist()


def rings(geom, left, top):
    result = []
    for part in shapely.get_parts(geom):
        for ring in (part.exterior, *part.interiors):
            coords = np.asarray(ring.coords)
            points = np.rint((coords - [left, top]) * [1, -1]).astype("int32")
            keep = np.r_[True, (np.diff(points, axis=0) != 0).any(axis=1)]
            points = points[keep]
            if len(points) >= 4:
                result.append(points[:-1].reshape(-1).tolist())
    return result


def build_layer(frame, name, mode, code, seats, labels, output):
    frame = frame.sort_values("pid", ignore_index=True)
    frame["pid"] = frame.pid.astype(str)
    fields, definitions = elections(frame, labels)
    value = frame[fields].fillna(0).to_numpy(dtype=np.int32).tolist()
    covered = frame.pos25.notna().to_list() if mode == "circuitos" else [None] * len(frame)
    projected = frame.to_crs(3857)
    left, bottom, right, top = projected.total_bounds
    stride = 2 if max(right - left, top - bottom) < 140_000 else 4
    reduced = projected.geometry.simplify(stride, preserve_topology=True)
    units = []
    for ix, row in enumerate(frame.itertuples()):
        shape = rings(reduced.iloc[ix], left, top) or rings(projected.geometry.iloc[ix], left, top)
        if not shape:
            raise ValueError(f"{code}/{mode}: unidad {row.pid} sin geometría dibujable")
        units.append([row.pid, row.circ if mode == "radios" else row.pid, int(row.population),
                      int(row.distrito), value[ix], shape, covered[ix]])
    signature = hashlib.sha256(json.dumps(
        [[unit[0], unit[1], unit[2], unit[3], unit[4], unit[6]] for unit in units],
        separators=(",", ":"),
    ).encode()).hexdigest()[:16]
    lat = float(frame.total_bounds[[1, 3]].mean())
    blob = {"id": code, "modo": mode, "nombre": name, "bancas": seats, "version": signature,
            "ancho": math.ceil(right - left), "alto": math.ceil(top - bottom),
            "escala": math.cos(math.radians(lat)), "elecciones": definitions,
            "unidades": units, "vecinos": neighbors(frame.geometry)}
    filename = f"{code}-{mode}.js"
    write_js(output / filename, "recibirBase", blob)
    return len(units), sum(unit[2] for unit in units)


def build_data(archive_path, data_path):
    data_path.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path) as archive, TemporaryDirectory() as scratch:
        control = json.loads(archive.read("CONTROL.json"))
        index = []
        for entry in sorted(name for name in archive.namelist() if name.endswith(".gpkg")):
            code = Path(entry).stem.split("_", 1)[0]
            info = control["jurisdicciones"][code]
            name = "Ciudad de Buenos Aires" if code == "01" else info["provincia"]
            count = info["bancas"]
            path = Path(archive.extract(entry, scratch))
            data = {}
            for mode, layer in GEOMETRY.items():
                frame = gpd.read_file(path, layer=layer)
                units, pop = build_layer(frame, name, mode, code, count, control["campos"], data_path)
                key = "poblacion_radios" if mode == "radios" else "poblacion_circuitos_estimada"
                if units != info[mode] or pop != info[key]:
                    raise ValueError(f"{code}/{mode}: recuento o población inesperados")
                data[mode] = units
            path.unlink()
            index.append({"id": code, "nombre": name, "bancas": count, **data})
            print(code, name, count, data, flush=True)
    if len(index) != 24 or sum(entry["bancas"] for entry in index) != 257:
        raise ValueError("El reparto no corresponde a las 24 jurisdicciones y los 257 distritos")
    write_js(data_path / "catalogo.js", "recibirCatalogo", index)


def package(output, data_only, skip_data):
    output.mkdir(parents=True, exist_ok=True)
    if not skip_data:
        build_data(SOURCE, output / "datos")
    if data_only:
        return
    for name in ARTIFACTS:
        shutil.copy2(HERE / name, output / name)
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    for name in FONT_FILES:
        shutil.copy2(ROOT / "mapas/mapa2003alt/assets" / name, assets / name)
    write_palette(output / "datos/colores.js")
    preparar_locales(output / "datos", write_js)
    if len(list((output / "datos").glob("*.js"))) != 52:
        raise ValueError("Faltan archivos de datos para empaquetar el editor")
    files = [output / name for name in ARTIFACTS + ["control_pba.json"]]
    files += [assets / name for name in FONT_FILES] + sorted((output / "datos").glob("*.js"))
    with ZipFile(output.parent / "editor_uninominal.zip", "w", ZIP_DEFLATED, compresslevel=5) as zipfile:
        for path in files:
            zipfile.write(path, Path("editor_uninominal") / path.relative_to(output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=OUTPUT)
    flags = parser.add_mutually_exclusive_group()
    flags.add_argument("--solo-datos", action="store_true")
    flags.add_argument("--con-datos-existentes", action="store_true")
    args = parser.parse_args()
    package(args.salida.resolve(), args.solo_datos, args.con_datos_existentes)
