"""ICG de la UTDT como prior del voto al oficialismo (28-oct-2026). Microdatos de la base histórica de la UTDT
(datos/icg/icg_microdatos.dta, copiada de la descarga oficial; codebook en datos/icg/codebook_icg.pdf).
ICG de cada elección = promedio ponderado (ponderacion_UTDT) de las entrevistas hechas entre 45 y 7 días antes de
la elección: lo que se conoce antes de la noche. Voto al oficialismo: % de votos positivos de la fuerza del gobierno
(1.a vuelta en presidenciales; diputados nacionales en legislativas), de las tablas de la Wikipedia.
    python -X utf8 proyeccion/icg/icg_voto.py
Salida: proyeccion/icg/elecciones.csv, loo.csv y una tabla en pantalla."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
# fecha, tipo, fuerza del gobierno, % positivos (fuente)
ELEC = [("2003-04-27", "P", "Kirchner (FPV, candidato de Duhalde)", 22.25),
        ("2005-10-23", "L", "Frente para la Victoria", 38.63),      # mapeo_listas_2005 (bloques de la Wikipedia)
        ("2007-10-28", "P", "Cristina Fernández (FPV)", 45.29),
        ("2009-06-28", "L", "Frente para la Victoria", 28.69),
        ("2011-10-23", "P", "Cristina Fernández (FPV)", 54.11),
        ("2013-10-27", "L", "Frente para la Victoria", 32.83),
        ("2015-10-25", "P", "Scioli (FPV)", 37.08),
        ("2017-10-22", "L", "Cambiemos", 41.75),
        ("2019-10-27", "P", "Macri (Juntos por el Cambio)", 40.28),
        ("2021-11-14", "L", "Frente de Todos", 33.97),               # mapeo_listas_2021
        ("2023-10-22", "P", "Massa (Unión por la Patria)", 36.78),
        ("2025-10-26", "L", "La Libertad Avanza", 40.66)]
REG = {1: "AMBA", 2: "Pampeana", 3: "Cuyo", 4: "NOA", 5: "NEA", 6: "Patagonia"}


def micro():
    f = os.path.join(HERE, "micro.pkl")
    if os.path.exists(f):
        return pd.read_pickle(f)
    d = pd.read_stata(os.path.join(ROOT, "datos", "icg", "icg_microdatos.dta"), convert_categoricals=False,
                      columns=["ola", "año", "mes", "dia", "Ciudad", "Zona", "Region", "ICG", "ponderacion_UTDT"])
    d = d.dropna(subset=["año", "mes"])
    d["fecha"] = pd.to_datetime(dict(year=d["año"].astype(int), month=d.mes.astype(int),
                                     day=d.dia.fillna(15).clip(1, 28).astype(int)), errors="coerce")
    d["w"] = d.ponderacion_UTDT.fillna(1.0)
    d.to_pickle(f)
    return d


def icg_ventana(d, fecha, a=45, b=7, por=None):
    f = pd.Timestamp(fecha)
    x = d[(d.fecha >= f - pd.Timedelta(days=a)) & (d.fecha <= f - pd.Timedelta(days=b)) & d.ICG.notna()]
    if por is None:
        return np.average(x.ICG, weights=x.w), len(x)
    return x.groupby(por).apply(lambda g: pd.Series(dict(icg=np.average(g.ICG, weights=g.w), n=len(g))))


def loo(df, cols):
    """Error de dejar una elección afuera, regresión lineal del voto en cols."""
    e = []
    for i in range(len(df)):
        tr = df.drop(df.index[i])
        X = np.c_[np.ones(len(tr)), tr[cols].to_numpy(float)]
        b = np.linalg.lstsq(X, tr.voto.to_numpy(float), rcond=None)[0]
        e.append(np.r_[1, df[cols].iloc[i].to_numpy(float)] @ b - df.voto.iloc[i])
    return np.array(e)


def main():
    d = micro()
    rows = []
    for fecha, tipo, fuerza, voto in ELEC:
        icg, n = icg_ventana(d, fecha)
        rows.append(dict(fecha=fecha, tipo=tipo, fuerza=fuerza, voto=voto, icg=icg, n=n))
    df = pd.DataFrame(rows)
    df["pres"] = (df.tipo == "P").astype(float)
    df["prev"] = df.voto.shift(1)                       # la elección nacional anterior
    df.to_csv(os.path.join(HERE, "elecciones.csv"), index=False)
    print(df.round(2).to_string(index=False))
    print("\ncorrelación ICG-voto %.2f" % df[["icg", "voto"]].corr().iloc[0, 1])
    b = np.polyfit(df.icg, df.voto, 1)
    print("voto = %.1f + %.1f × ICG" % (b[1], b[0]))
    R = {}
    R["ICG"] = loo(df, ["icg"])
    R["ICG + presidencial"] = loo(df, ["icg", "pres"])
    R["promedio histórico"] = loo(df, [])
    s = df.iloc[1:]
    R["elección anterior"] = (s.prev - s.voto).to_numpy()
    out = []
    for k, e in R.items():
        out.append(dict(modelo=k, mae=np.abs(e).mean(), rmse=np.sqrt((e ** 2).mean()), max=np.abs(e).max()))
    print("\nDejando una elección afuera (puntos de voto al oficialismo):")
    print(pd.DataFrame(out).round(2).to_string(index=False))
    L = pd.DataFrame({k: pd.Series(v, index=(df.fecha if len(v) == len(df) else s.fecha)) for k, v in R.items()})
    L.round(2).to_csv(os.path.join(HERE, "loo.csv"))
    print(L.round(1).to_string())


if __name__ == "__main__":
    main()
