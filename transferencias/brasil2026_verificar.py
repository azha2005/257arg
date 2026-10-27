"""Controles independientes de alineación, masas, marginales y entregables."""
import json
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from brasil2026_datos import OUT, dump
from brasil2026_estimar import NIVELES, aggregate, con_regiones, unidades


def main():
    ctl = json.loads((OUT/"control.json").read_text(encoding="utf8"))
    A, B, meta = pd.read_pickle(OUT/"pareadas.pkl")
    M = pd.read_csv(OUT/"matriz_votos.csv", index_col=0)
    intervals = pd.read_csv(OUT/"intervalos.csv")
    pp = pd.read_csv(OUT/"por_provincia.csv", keep_default_na=False).rename(columns={"distrito": "uf"})
    pr = pd.read_csv(OUT/"por_region.csv", dtype=str, keep_default_na=False) if ctl["nivel"] != "uf" else None
    assert A.index.equals(B.index) and A.index.equals(meta.index)
    assert A.index.is_unique and B.index.is_unique
    assert M.index.tolist() == A.columns.tolist() and M.columns.tolist() == B.columns.tolist()
    assert np.isfinite(M.to_numpy()).all() and M.ge(0).all().all()
    assert abs(M.to_numpy().sum()-ctl["electores"]) <= M.size/2+1
    assert (B.sum(axis=1)-A.sum(axis=1)).abs().le(5).all()
    assert ((B.sum(axis=1)-A.sum(axis=1)).abs()/A.sum(axis=1)).le(.01).all()
    assert intervals.p5.le(intervals.p95).all() and intervals.p5.ge(0).all()
    assert intervals.min_modelos.le(intervals.votos).all() and intervals.max_modelos.ge(intervals.votos).all()
    assert set(pp.uf) == set(ctl["ufs"]) and len(ctl["ufs"]) == 28
    byuf = pp.groupby(["origen", "destino"]).votos.sum().unstack().reindex(index=M.index, columns=M.columns)
    assert np.abs(byuf.to_numpy()-M.to_numpy()).max() <= len(ctl["ufs"])/2+1
    if pr is not None:
        pr["votos"] = pr.votos.astype(float)
        byreg = pr.groupby(["origen", "destino"]).votos.sum().unstack().reindex(index=M.index, columns=M.columns)
        assert np.abs(byreg.to_numpy()-M.to_numpy()).max() <= pr.region.nunique()/2+1
        assert pr.region.nunique() == ctl["regiones"][ctl["nivel"]]
    regiones = pd.read_csv(OUT/"regiones_municipio.csv", dtype=str)
    assert not regiones.duplicated(["SG_UF", "CD_MUNICIPIO"]).any() and regiones[list(NIVELES.values())].notna().all().all()
    for b in ctl["celdas_borde"]:
        assert 100*M.loc[b["origen"], b["destino"]]/M.loc[b["origen"]].sum() < ctl["umbral_borde_pp"] + .01
    source_model = (A.div(A.sum(axis=1), axis=0).mul(B.sum(axis=1), axis=0)).sum()
    assert np.abs(M.sum(axis=1)-source_model).max() <= len(M.columns)/2+1
    assert B.sum().astype(int).to_dict() == ctl["marginal_destino"]
    for field in ["local", "munzona"]:
        a, b, _ = aggregate(A, B, meta, field)
        assert np.allclose(a.sum(), A.sum()) and np.allclose(b.sum(), B.sum())
    U = unidades(A, B, con_regiones(meta))
    check = pd.DataFrame({"municipio": meta.municipio.to_numpy(), "fold": U["fold"]}).groupby("municipio").fold.nunique()
    assert check.eq(1).all(), "Fuga territorial entre folds"
    strictA, strictB, _ = pd.read_pickle(OUT/"pareadas_estrictas.pkl")
    assert np.array_equal(strictA.sum(axis=1), strictB.sum(axis=1))
    exclusion = pd.read_csv(OUT/"exclusiones.csv", dtype={k:str for k in A.index.names}).set_index(A.index.names)
    assert len(exclusion.index.intersection(A.index)) == 0
    cov = pd.read_csv(OUT/"cobertura_por_uf.csv")
    assert cov.electores_usados.sum() == ctl["electores"]
    assert len(A)+len(exclusion) == 499248
    official = json.loads((OUT/"cotejo_totales_tse.json").read_text(encoding="utf8"))
    assert all(check["diferencia"] == 0 for turn in official for check in turn["checks"].values())
    ET.parse(OUT/"sankey_brasil_2026p_2026b.svg")
    report = dict(estado="OK", secciones=len(A), exclusiones=len(exclusion), electores=ctl["electores"], cobertura_destino_pct=100*cov.electores_usados.sum()/cov.electores_2.sum(), error_redondeo_total=int(M.to_numpy().sum()-ctl["electores"]), controles=["alineacion y unicidad", "tolerancia padron", "masas y fuente reescalada", "marginales nacionales y por UF", "intervalos ordenados", "agregaciones conservan votos", "municipios no cruzan folds", "version estricta", "exclusiones disjuntas y exhaustivas", "cotejo oficial", "SVG XML valido", "regiones IBGE completas y anidadas", "suma por region", "rango de modelos contiene la principal", "celdas en el borde"])
    dump(OUT/"VERIFICACION.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
