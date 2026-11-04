"""Sondas de revision metodologica. No modifica modelos ni resultados operativos.
Ejecutar desde la raiz: python -X utf8 proyeccion/revision_astra_20261028/auditar.py
Los casos sinteticos se identifican expresamente en resultados.json.
"""
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROY = HERE.parent
sys.path.insert(0, str(PROY))
sys.path.insert(0, str(PROY / "icg"))
import backtest as bt
import fotos_modelo as fm
import proyectar_fotos as pf
import congreso as cg
import icg_fotos as icg


def quiet_calc(a, nboot=400):
    with contextlib.redirect_stdout(io.StringIO()):
        return pf.calcular(a, "2023p,2021bl", nboot=nboot, seed=928)


def main():
    out = {"alcance": "Revision local 2026-10-28; sondas, no validacion prospectiva"}
    out["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                     [PROY / n for n in ["backtest.py", "aguja.py", "fotos_modelo.py",
                                         "proyectar_fotos.py", "congreso.py", "fotos_sim.py"]]}
    universos = []
    for ori, des, circ in [("2015p", "2015b", False), ("2023p", "2023b", False),
                           ("2019p", "2023p", True), ("2021bl", "2023p", True),
                           ("2023p", "2025bl", True)]:
        bt.Y0, bt.Y1, bt.CIRC = ori, des, circ
        m, e, X, Y, dpart, dcols, ocols, info = bt.prepare()
        full, _, _ = bt.load(des, .01)
        raw = pd.read_pickle(PROY / ("mesas_%s.pkl" % des))
        pos = [c for c in raw if c not in bt.KEY + ["e"] + bt.FIXED]
        full_votes = raw[pos].sum()
        included = Y[:, [dcols.index(c) for c in dpart]].sum(1) * e
        all_positive = [dcols.index(c) for c in dcols if c not in ["BLANCO/NULO", "ABSTENCION"]]
        matched_votes = (Y[:, all_positive] * e[:, None]).sum()
        winner = full_votes.idxmax()
        w = (Y[:, dcols.index(winner)] * e).sum()
        missing = sorted(set(raw.distrito_id) - set(m.distrito_id))
        universos.append(dict(par=ori + "->" + des, **info, distritos_ausentes=missing,
                              cobertura_votos_positivos=matched_votes/full_votes.sum(),
                              ganador=winner, porcentaje_universo_completo=100*full_votes[winner]/full_votes.sum(),
                              porcentaje_cruce_todos_positivos=100*w/matched_votes,
                              porcentaje_objetivo_backtest=100*w/included.sum()))
    out["universo_backtest"] = universos
    print("Universos", json.dumps(universos, ensure_ascii=False), flush=True)

    a = pf.leer(PROY / "fotos25/actas.csv")
    R = quiet_calc(a)
    F = R["F"]
    e = F.e.to_numpy(float)
    w = fm.poststrat(e, R["s_f"], R["share"])
    y = np.vstack(F.y)
    pesos = []
    for j, b in enumerate(R["blocs"]):
        seen = np.isfinite(y[:, j])
        pesos.append(dict(fuerza=b, actas=int(seen.sum()),
                          peso_amba=100*w[seen & (R["s_f"] == "AMBA")].sum()/w[seen].sum()))
    out["actas_reales"] = dict(n=len(F), circuitos=len(np.unique(R["clus"])),
                                objetivo_amba=100*R["share"]["AMBA"], pesos_por_fuerza=pesos,
                                punto=dict(zip(R["blocs"], R["pt"])))
    # La misma acta con otro nombre de imagen: prueba de identidad, sin votos nuevos.
    keys = a.mesa_key.unique()
    first = keys[0]
    dup = a[a.mesa_key == first].copy()
    dup["foto"] = "COPIA_MISMA_ACTA.jpg"
    dup["mesa_key"] = dup.foto + "|" + dup.distrito_id + "|" + dup.seccion_id.astype(str) + "|" + dup.circuito + "|" + dup.mesa
    RD = quiet_calc(pd.concat([a, dup], ignore_index=True), nboot=100)
    out["duplicado_sintetico"] = dict(n_original=len(F), n_con_copia=len(RD["F"]),
                                       cambio_pp=dict(zip(R["blocs"], RD["pt"]-R["pt"])))
    # Observacion parcial sintetica: PU solo visible en un circuito de los reales.
    masked = a.copy()
    keeper = masked[masked.bloque == "PU"].iloc[0]
    keep = ((masked.distrito_id == keeper.distrito_id) & (masked.seccion_id == keeper.seccion_id)
            & (masked.circuito == keeper.circuito))
    masked = masked[keep | (masked.bloque != "PU")].copy()
    masked["completa"] = "no"
    RM = quiet_calc(masked)
    out["parcial_sintetico"] = dict(n=len(RM["F"]),
                                    punto_finito=bool(np.isfinite(RM["pt"]).all()),
                                    remuestras_finitas=int(np.isfinite(RM["bs"]).all(1).sum()),
                                    nboot=len(RM["bs"]),
                                    banda_finita=bool(np.isfinite(RM["lo"]).all()),
                                    probabilidad_que_reportaria=float((RM["marg"] > 0).mean()))
    # Nacional mostrado frente al que implican los votos usados para las bancas.
    D = R["proj_d"](np.arange(len(F)))[R["blocs"]]
    G, _ = cg.provinciales(D, 2025, a)
    out["nacional_y_congreso"] = dict(
        nacional=dict(zip(R["blocs"], R["pt"])),
        agregado_distritos_antes=(100*D.sum()/D.sum().sum()).to_dict(),
        agregado_distritos_despues=(100*G.sum()/G.sum().sum()).to_dict())
    official = cg.listas(2025)
    seats, _ = cg.repartir(G, 2025, R["pad"])
    zeroes = []
    for force in ["LLA", "FP", "PU", "FIT"]:
        absent = [d for d in G.index if d not in set(official.loc[official.fuerza == force, "distrito"])]
        zeroes.append(dict(fuerza=force, distritos_sin_lista=absent,
                           votos_proyectados_sin_lista=float(G.loc[absent, force].sum()),
                           bancas_proyectadas_sin_lista=sum(seats[d].get(force, 0) for d in absent)))
    out["disponibilidad_listas"] = zeroes
    # Una foto parcial con solo LLA y FP no informa cero PU.
    unit = pd.DataFrame({"LLA": [4000.], "FP": [3500.], "PU": [1500.], "OTRAS": [1000.]}, index=["04"])
    partial = pd.DataFrame({"distrito_id": ["04", "04"], "bloque": ["LLA", "FP"],
                            "lista": ["LLA", "FP"], "votos": [1000., 1000.], "completa": ["no", "no"]})
    prior, _ = cg.provinciales(unit, 2025)
    after, _ = cg.provinciales(unit, 2025, partial)
    out["provincial_parcial_sintetico"] = dict(PU_sin_actas_pct=100*prior.loc["04", "PU"]/prior.sum().sum(),
                                               PU_con_acta_que_no_informa_PU_pct=100*after.loc["04", "PU"]/after.sum().sum())
    # Probabilidad pareada vs ser primero, en tres remuestras sinteticas de tres partidos.
    draws = np.array([[40., 30., 30.], [35., 25., 40.], [36., 34., 30.]])
    out["probabilidad_sintetica_tres_fuerzas"] = dict(p_supera_segundo=float((draws[:,0]>draws[:,1]).mean()),
                                                     p_primero=float((draws.argmax(1)==0).mean()))
    # ICG: dejar un año fuera no equivale a entrenar solo con el pasado.
    base = pd.read_csv(PROY / "icg/elecciones.csv")
    priors = []
    for fecha in ["2019-10-27", "2021-11-14", "2023-10-22", "2025-10-26"]:
        loo, sd = icg.prior(fecha)
        forward, sdf = icg.prior(fecha, base[base.fecha < fecha])
        priors.append(dict(fecha=fecha, prior_loo=loo, prior_solo_pasado=forward,
                           real=float(base.set_index("fecha").loc[fecha, "voto"]),
                           elecciones_futuras_en_loo=base.loc[base.fecha > fecha, "fecha"].tolist()))
    out["icg_temporal"] = priors
    # Diagnosticos sobre resultados YA guardados; no recalibran la produccion.
    models = []
    for pair in ["2015p_2015b", "2023p_2023b", "2019p_2023p_circuito"]:
        df = pd.read_csv(PROY / pair / "corridas.csv")
        df = df[df.corte <= .25]
        mae = df.assign(abs_error=df.err_nac.abs()).groupby("metodo").abs_error.mean()
        models.append(dict(par=pair, cortes="0.2 a 25 por ciento", mae=mae.reindex(
            ["D", "D_sin_ajuste", "E_sin_ajuste"]).to_dict()))
    out["comparacion_modelos_existentes"] = models
    bands = []
    for path in sorted((PROY / "fotos_sim").glob("*_n30.csv")):
        df = pd.read_csv(path)
        df = df[(df.metodo == "Goodman lam=0,1 + AMBA/resto") & df.z.notna()]
        for scheme, g in df.groupby("esquema"):
            bands.append(dict(par=path.stem, esquema=scheme, n=len(g), factor95=float(g.z.quantile(.95)),
                              cobertura_aproximada_simetrica_1_4=float((g.z <= 1.4).mean())))
    out["bandas_diagnostico_no_cobertura_pipeline"] = bands
    # Guardar resultados con numeros estandar JSON, sin NaN.
    (HERE / "resultados.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k not in ("sha256", "universo_backtest")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
