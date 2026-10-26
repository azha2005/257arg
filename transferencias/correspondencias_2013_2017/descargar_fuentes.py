"""Preserva las normas consultadas y los anexos enlazados por Infoleg."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import hashlib
import json
import requests

HERE = Path(__file__).resolve().parent
SOURCES = {
    "nqn_disp154_2016": "https://www.argentina.gob.ar/normativa/nacional/norma-271230/texto",
    "tdf_ley1186_2017": "https://www.argentina.gob.ar/normativa/provincial/ley-1186-123456789-0abc-defg-186-1000vvorpyel/actualizacion",
    "sc_cne68_2022": "https://www.boletinoficial.gob.ar/detalleAviso/primera/272295/20220923",
    "sc_res28_2024": "https://www.argentina.gob.ar/normativa/nacional/norma-402921/texto",
    "rn_habiles_2017": "https://old.pjn.gov.ar/cne/secelec/document/otros/16-Habiles_Mesas.pdf",
    "sf_res543_2015": "https://www.argentina.gob.ar/normativa/nacional/norma-246080/texto",
    "rn_res186_2022": "https://www.argentina.gob.ar/normativa/nacional/norma-376317/texto",
    "sf_res66_2022": "https://www.argentina.gob.ar/normativa/nacional/norma-373111/texto",
    "rn_res613_2015": "https://www.argentina.gob.ar/normativa/nacional/norma-246380/texto",
    "rn_disp194_2015": "https://www.argentina.gob.ar/normativa/nacional/norma-246982/texto",
    "rn_res92_2024": "https://www.argentina.gob.ar/normativa/nacional/norma-399114/texto",
    "sl_disp38_2015": "https://www.argentina.gob.ar/normativa/nacional/norma-248942/texto",
    "sl_res651_2016": "https://www.argentina.gob.ar/normativa/nacional/norma-261558/texto",
    "sl_res376_2018": "https://www.argentina.gob.ar/normativa/nacional/norma-312228/texto",
    "sl_res187_2022": "https://www.argentina.gob.ar/normativa/nacional/norma-376149/texto",
    "tdf_disp8_2017": "https://www.argentina.gob.ar/normativa/nacional/norma-271231/texto",
    "tdf_res291_2017": "https://www.argentina.gob.ar/normativa/nacional/norma-274819/texto",
}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))


def fetch(item):
    name, url = item
    r = requests.get(url, timeout=15 if "old.pjn.gov.ar" in url else 45)
    r.raise_for_status()
    if r.content.startswith(b"%PDF"):
        filename = name + ".pdf"
        (HERE / filename).write_bytes(r.content)
        print(name, "PDF OK", flush=True)
        return {"id": name, "url": url, "consulta": "2026-10-26", "archivo": filename,
                "sha256": hashlib.sha256(r.content).hexdigest()}
    (HERE / (name + ".html")).write_text(r.text, encoding="utf8")
    p = Text()
    p.feed(r.text)
    (HERE / (name + ".txt")).write_text("\n".join(p.text), encoding="utf8")
    result = {"id": name, "url": url, "consulta": "2026-10-26", "sha256": hashlib.sha256(r.content).hexdigest(), "anexos": []}
    links = list(dict.fromkeys(urljoin(url, a) for a in p.links if "/archivo" in a or a.lower().endswith(".pdf")))
    for i, link in enumerate(links):
        a = requests.get(link, timeout=45)
        a.raise_for_status()
        filename = name + f"_anexo{i+1}.pdf"
        (HERE / filename).write_bytes(a.content)
        result["anexos"].append({"url": link, "archivo": filename, "sha256": hashlib.sha256(a.content).hexdigest()})
    print(name, "OK", len(links), "anexos", flush=True)
    return result


def safe_fetch(item):
    try:
        return fetch(item)
    except requests.RequestException as error:
        print(item[0], "NO DESCARGADO:", type(error).__name__, flush=True)
        return {"id": item[0], "url": item[1], "consulta": "2026-10-26", "descarga": "fallida",
                "error": type(error).__name__}


if __name__ == "__main__":
    with ThreadPoolExecutor(3) as pool:
        results = list(pool.map(safe_fetch, SOURCES.items()))
    (HERE / "fuentes.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf8")
