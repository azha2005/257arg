"""Enlace historico sin eliminar unidades destino. Solo utiliza votos del origen."""
import numpy as np
import pandas as pd


def alinear(marco, origen, columnas, pesos, niveles):
    """Proporciones de origen para cada fila destino y nivel de respaldo utilizado.

    niveles: claves de mas a menos precisas. La ultima opcion es el total del origen.
    El marco puede incluir unidades nuevas; nunca se usan sus votos para el enlace.
    """
    weights = np.asarray(pesos, float)
    values = origen[columnas].to_numpy(float)
    valid = np.isfinite(values).all(1) & (weights > 0)
    if not valid.any():
        raise ValueError("No hay unidades historicas validas")
    src = origen.loc[valid].reset_index(drop=True).copy()
    w = weights[valid]
    v = values[valid]
    # Nombres internos separados de los nombres de partidos.
    vc = ["__v%d" % j for j in range(len(columnas))]
    src[vc] = v * w[:, None]
    src["__peso"] = w
    out = np.full((len(marco), len(columnas)), np.nan)
    nivel = np.full(len(marco), "nacional", dtype=object)
    for name, keys in niveles:
        grouped = src.groupby(keys, dropna=False)[vc + ["__peso"]].sum()
        tab = grouped[vc].div(grouped["__peso"], axis=0)
        ix = (pd.MultiIndex.from_frame(marco[keys]) if len(keys) > 1 else pd.Index(marco[keys[0]]))
        candidate = tab.reindex(ix).to_numpy(float)
        fill = ~np.isfinite(out).all(1) & np.isfinite(candidate).all(1)
        out[fill], nivel[fill] = candidate[fill], name
    missing = ~np.isfinite(out).all(1)
    out[missing] = np.average(v, weights=w, axis=0)
    return out, nivel
