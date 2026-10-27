"""Municipio TSE → región geográfica inmediata e intermedia del IBGE (división de 2017).

Fuentes en datos_oficiales/brasil2026/ibge/: tabla oficial del IBGE (geoftp, composición por municipios 2017)
y la correspondencia de códigos TSE↔IBGE de github.com/betafcc/Municipios-Brasileiros-TSE. Los 23 nombres que
difieren entre ambas son variantes de grafía (D OESTE / DO OESTE, MELLO / MELO) o cambios de nombre (Joca Claudino,
ex Santarém PB); se conservan los códigos. Boa Esperança do Norte (MT, instalado en 2025) no está en ninguna de las dos:
se desmembró de Sorriso y Nova Ubiratã, que están en la misma región inmediata (510008 Sorriso), y va a esa.
El exterior (ZZ) no tiene regiones: queda como una sola región.
    python -X utf8 transferencias/brasil2026_regiones.py
Salida: brasil_2026p_2026b/regiones_municipio.csv"""
import hashlib
import json

import pandas as pd

from brasil2026_datos import OUT, RAW

IBGE = RAW / "ibge"
TABLA = IBGE / "regioes_geograficas_composicao_por_municipios_2017_20180911.xlsx"
CRUCE = IBGE / "municipios_brasileiros_tse.csv"
URLS = {TABLA.name: "https://geoftp.ibge.gov.br/organizacao_do_territorio/divisao_regional/divisao_regional_do_brasil/divisao_regional_do_brasil_em_regioes_geograficas_2017/tabelas/regioes_geograficas_composicao_por_municipios_2017_20180911.xlsx",
        CRUCE.name: "https://raw.githubusercontent.com/betafcc/Municipios-Brasileiros-TSE/master/municipios_brasileiros_tse.csv"}
NUEVOS = {"73709": "510008"}  # Boa Esperança do Norte → región inmediata de Sorriso


def main():
    manifest = {name: dict(url=url, sha256=hashlib.sha256((IBGE / name).read_bytes()).hexdigest()) for name, url in URLS.items()}
    (IBGE / "fuentes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf8")
    reg = pd.read_excel(TABLA, dtype=str)
    cruce = pd.read_csv(CRUCE, dtype=str)
    _, _, meta = pd.read_pickle(OUT / "pareadas.pkl")
    mun = meta.reset_index()[["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"]].drop_duplicates()
    assert not mun.duplicated(["SG_UF", "CD_MUNICIPIO"]).any()
    m = mun.merge(cruce[["codigo_tse", "uf", "codigo_ibge"]], left_on="CD_MUNICIPIO", right_on="codigo_tse", how="left")
    m = m.merge(reg, left_on="codigo_ibge", right_on="CD_GEOCODI", how="left")
    rgi = reg.drop_duplicates("cod_rgi").set_index("cod_rgi")
    for tse, cod in NUEVOS.items():
        k = m.CD_MUNICIPIO.eq(tse)
        m.loc[k, ["cod_rgi", "nome_rgi", "cod_rgint", "nome_rgint"]] = [cod, rgi.at[cod, "nome_rgi"], rgi.at[cod, "cod_rgint"], rgi.at[cod, "nome_rgint"]]
    ext = m.SG_UF.eq("ZZ")
    m.loc[ext, ["cod_rgi", "nome_rgi", "cod_rgint", "nome_rgint"]] = ["ZZ", "Exterior", "ZZ", "Exterior"]
    assert m.cod_rgi.notna().all(), m[m.cod_rgi.isna()]
    assert (m.uf.isna() | m.uf.eq(m.SG_UF)).all()
    # La región inmediata está dentro de la intermedia y ambas dentro de la UF.
    assert m.groupby("cod_rgi").cod_rgint.nunique().eq(1).all() and m.groupby("cod_rgint").SG_UF.nunique().eq(1).all()
    out = m[["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "codigo_ibge", "cod_rgi", "nome_rgi", "cod_rgint", "nome_rgint"]]
    out.to_csv(OUT / "regiones_municipio.csv", index=False, encoding="utf-8-sig")
    print("municipios", len(out), "inmediatas", out.cod_rgi.nunique(), "intermedias", out.cod_rgint.nunique())


if __name__ == "__main__":
    main()
