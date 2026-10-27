"""Descarga y prepara las dos vueltas presidenciales oficiales del TSE 2026."""
import concurrent.futures
import hashlib
import json
import pathlib
import sys
import zipfile
from datetime import datetime, timezone

import pandas as pd
import requests

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parent / "datos_oficiales" / "brasil2026"
OUT = HERE / "brasil_2026p_2026b"
KEY = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
UF_NOMBRES = dict(AC="Acre", AL="Alagoas", AM="Amazonas", AP="Amapá", BA="Bahia", CE="Ceará", DF="Distrito Federal", ES="Espírito Santo", GO="Goiás", MA="Maranhão", MG="Minas Gerais", MS="Mato Grosso do Sul", MT="Mato Grosso", PA="Pará", PB="Paraíba", PE="Pernambuco", PI="Piauí", PR="Paraná", RJ="Rio de Janeiro", RN="Rio Grande do Norte", RO="Rondônia", RR="Roraima", RS="Rio Grande do Sul", SC="Santa Catarina", SE="Sergipe", SP="São Paulo", TO="Tocantins", ZZ="Exterior")
URLS = {
    "votos": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip?verificacion=20261026",
    "detalle": "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip?verificacion=20261026",
}


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf8")


def download(item):
    name, url = item
    dest = RAW / f"{name}.zip"
    meta = RAW / f"{name}.json"
    if dest.exists() and meta.exists():
        saved = json.loads(meta.read_text(encoding="utf8"))
        assert hashlib.file_digest(dest.open("rb"), "sha256").hexdigest() == saved["sha256"]
        print(name, "ZIP local verificado", flush=True)
        return
    tmp = dest.with_suffix(".part")
    digest = hashlib.sha256()
    with requests.get(url, stream=True, timeout=(30, 120)) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for part in r.iter_content(2**20):
                f.write(part)
                digest.update(part)
        if r.headers.get("Content-Length"):
            assert tmp.stat().st_size == int(r.headers["Content-Length"])
        metadata = {"url": url, "fecha_utc": datetime.now(timezone.utc).isoformat(), "headers": dict(r.headers), "sha256": digest.hexdigest(), "bytes": tmp.stat().st_size}
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        metadata["miembros"] = z.namelist()
        import fitz
        with fitz.open(stream=z.read("leiame.pdf"), filetype="pdf") as pdf:
            (RAW / f"leiame_{name}.txt").write_text("\n".join(p.get_text() for p in pdf), encoding="utf8")
    tmp.replace(dest)
    dump(meta, metadata)
    print(name, "descargado", metadata["bytes"], digest.hexdigest(), flush=True)


def prepare():
    OUT.mkdir(exist_ok=True)
    votes = []
    names = []
    with zipfile.ZipFile(RAW / "votos.zip") as z, z.open("votacao_secao_2026_BR.csv") as f:
        use = KEY + ["CD_CARGO", "NR_VOTAVEL", "NM_VOTAVEL", "QT_VOTOS", "SQ_CANDIDATO", "DT_GERACAO", "DT_ELEICAO"]
        for n, chunk in enumerate(pd.read_csv(f, sep=";", encoding="latin1", dtype=str, usecols=use, chunksize=300_000)):
            assert chunk.CD_CARGO.eq("1").all()
            chunk["QT_VOTOS"] = pd.to_numeric(chunk.QT_VOTOS)
            names.append(chunk[["NR_TURNO", "NR_VOTAVEL", "NM_VOTAVEL", "SQ_CANDIDATO", "DT_GERACAO", "DT_ELEICAO"]].drop_duplicates())
            votes.append(chunk.groupby(KEY + ["NR_VOTAVEL"], sort=False).QT_VOTOS.sum())
            if n % 5 == 0:
                print("carga votos", (n + 1) * 300_000, flush=True)
    v = pd.concat(votes).groupby(level=list(range(6)), sort=False).sum().unstack("NR_VOTAVEL", fill_value=0)
    pd.concat(names).drop_duplicates().sort_values(["NR_TURNO", "NR_VOTAVEL"]).to_csv(OUT / "candidatos_codigos.csv", index=False, encoding="utf-8-sig")
    with zipfile.ZipFile(RAW / "detalle.zip") as z, z.open("detalhe_votacao_secao_2026_BR.csv") as f:
        detail = pd.read_csv(f, sep=";", encoding="latin1", dtype=str)
    assert detail.CD_CARGO.eq("1").all()
    assert not detail.duplicated(KEY).any(), "Detalle duplicado: inspeccionar antes de modelar"
    detail = detail.set_index(KEY)
    nums = [c for c in detail if c.startswith("QT_")]
    detail[nums] = detail[nums].apply(pd.to_numeric)
    detail.to_pickle(OUT / "detalle.pkl")
    v.to_pickle(OUT / "votos.pkl")
    counts = detail.groupby(level=[0, 1])[nums].sum()
    counts.to_csv(OUT / "totales_oficiales_por_uf.csv", encoding="utf-8-sig")
    print("secciones detalle", len(detail), "votos", len(v), flush=True)
    print(counts.groupby(level=0).sum().to_string(), flush=True)


def compare_totals():
    d, v = pd.read_pickle(OUT / "detalle.pkl"), pd.read_pickle(OUT / "votos.pkl")
    results = []
    for turn, eid in [("1", 6257), ("2", 6258)]:
        path = RAW / f"total_oficial_{eid}.json"
        url = f"https://resultados.tse.jus.br/oficial/ele2026/{eid}/dados/br/br-c0001-e{eid:06d}-u.json"
        if not path.exists():
            r = requests.get(url, timeout=45)
            r.raise_for_status()
            path.write_text(r.text, encoding="utf8")
        j = json.loads(path.read_text(encoding="utf8"))
        a, b = d.xs(turn, level=0), v.xs(turn, level=0)
        official = {"QT_APTOS": int(j["e"]["te"]), "QT_COMPARECIMENTO": int(j["e"]["c"]), "QT_ABSTENCOES": int(j["e"]["a"]), "QT_VOTOS_NOMINAIS": int(j["v"]["vnom"])+int(j["v"]["vnt"]), "QT_VOTOS_BRANCOS": int(j["v"]["vb"]), "QT_VOTOS_NULOS": int(j["v"]["vn"])}
        checks = {k: {"csv": int(a[k].sum()), "json": val} for k, val in official.items()}
        seen = []
        for agr in j["carg"][0]["agr"]:
            for par in agr["par"]:
                for cand in par["cand"]:
                    seen.append(cand["n"])
                    checks[cand["nm"]] = {"csv": int(b[cand["n"]].sum()), "json": int(cand["vap"])}
        other = [c for c in b if c not in seen + ["95", "96"]]
        checks["codigos_no_en_listado_candidatos_json"] = {"csv": int(b[other].sum().sum()), "json": int(j["v"]["vnt"])}
        for check in checks.values():
            check["diferencia"] = check["csv"]-check["json"]
        assert all(c["diferencia"] == 0 for c in checks.values()), checks
        results.append(dict(turno=turn, url=url, checks=checks, nota="En primera vuelta, los 5246 del codigo 28 estan en vnt del JSON; el CSV los incluye en QT_VOTOS_NOMINAIS. No se reclasifica la fuente.", uf=sorted(a.index.get_level_values(0).unique()), generacion_json=[j["dg"], j["hg"]]))
    dump(OUT / "cotejo_totales_tse.json", results)
    print("Totales y candidatos: cierre exacto con JSON TSE; tratamiento de vnt documentado")


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    if "--cotejar" in sys.argv:
        compare_totals()
    elif "--preparar" in sys.argv:
        prepare()
    else:
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            list(pool.map(download, URLS.items()))
