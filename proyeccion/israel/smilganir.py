"""Baja el resultado parcial por urna del mapa de Nir Smilga (smilganir.github.io/isr-socio-elections, archivo publico
de GitHub Pages: results-snapshot/bundle.json, que replica el conteo del Comite) y lo pasa al formato de expb.csv
para vivo.py. Uso local: el archivo dice remotePublicationAllowed=false, asi que no se republican los datos.
    python -X utf8 proyeccion/israel/smilganir.py          # deja vivo_datos/expb_smilganir_<hora>.csv
    python -X utf8 proyeccion/israel/vivo.py proyeccion/israel/vivo_datos
Bajarlo como mucho cada pocos minutos."""
import os, sys, json, time, datetime, urllib.request
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://smilganir.github.io/isr-socio-elections/results-snapshot/bundle.json?v=%d"
OUT = os.path.join(HERE, "vivo_datos")


def main():
    raw = urllib.request.urlopen(urllib.request.Request(URL % time.time(), headers={"User-Agent": "Mozilla/5.0"}),
                                 timeout=60).read()
    b = json.loads(raw)
    cov = b.get("coverage", {})
    rows = []
    for v in b["kalpis_lookup"].values():
        k = v["kpi"]
        if k.get("src") != "real_results":
            continue
        r = {"סמל ישוב": int(v["semel"]), "שם ישוב": v.get("name", ""), "קלפי": float(v["kalpi"]),
             "בזב": k["bzb"], "מצביעים": k["voted"], "כשרים": k["kosher"]}
        r.update({p["code"]: p["votes"] for p in k["parties"]})
        rows.append(r)
    d = pd.DataFrame(rows).fillna(0)
    os.makedirs(OUT, exist_ok=True)
    hora = (cov.get("official_update") or datetime.datetime.now().strftime("%H:%M")).split()[-1].replace(":", "")
    path = os.path.join(OUT, "expb_smilganir_%s.csv" % hora)
    d.to_csv(path, index=False, encoding="utf-8-sig")
    print("%d urnas (de %s) · actualizacion oficial %s · validos %s -> %s" % (
        len(d), cov.get("final_ballots_total"), cov.get("official_update"), int(d["כשרים"].sum()), path))


if __name__ == "__main__":
    main()
