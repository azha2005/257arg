"""Inspecciona ZIP oficiales por HTTP Range, sin bajarlos completos."""
import concurrent.futures
import csv
import io
import json
import pathlib
import zipfile

import requests

URLS = {
    "presidente_seccion": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip",
    "detalle_seccion": "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip",
}


class RemoteZip(io.RawIOBase):
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        r = self.session.get(url, headers={"Range": "bytes=-65536"}, timeout=45)
        if r.status_code != 206:
            raise ValueError(f"Servidor no respeta Range inicial: {r.status_code}")
        self.headers = dict(r.headers)
        self.size = int(r.headers["Content-Range"].split("/")[-1])
        self.pos = 0
        self.downloaded = len(r.content)

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        self.pos = offset + (0 if whence == 0 else self.pos if whence == 1 else self.size)
        return self.pos

    def tell(self):
        return self.pos

    def read(self, n=-1):
        n = min(n if n >= 0 else self.size - self.pos, self.size - self.pos)
        if n <= 0:
            return b""
        if n > 2_000_000:
            raise ValueError("El sondeo no permite lecturas mayores a 2 MB")
        with self.session.get(self.url, headers={"Range": f"bytes={self.pos}-{self.pos+n-1}"}, stream=True, timeout=45) as r:
            if r.status_code != 206:
                raise ValueError(f"Servidor no respeta Range: {r.status_code}")
            if r.headers.get("ETag") != self.headers.get("ETag"):
                raise ValueError("El CDN cambio la version entre lecturas parciales")
            data = r.content
        self.downloaded += len(data)
        self.pos += len(data)
        return data


def probe(item):
    name, url = item
    remote = RemoteZip(url)
    result = {"url": url, "headers": remote.headers, "miembros": []}
    with zipfile.ZipFile(remote) as archive:
        for member in archive.infolist():
            entry = {"nombre": member.filename, "bytes": member.file_size, "fecha_zip": member.date_time}
            if member.filename.lower().endswith(".csv"):
                with archive.open(member) as source:
                    text = io.TextIOWrapper(source, encoding="latin1")
                    entry["muestra"] = [text.readline().rstrip("\r\n") for _ in range(3)]
                    if name.startswith("presidente"):
                        columns = next(csv.reader([entry["muestra"][0]], delimiter=";"))
                        examples = {}
                        for line in entry["muestra"][1:]:
                            row = dict(zip(columns, next(csv.reader([line], delimiter=";"))))
                            examples.setdefault(row["NR_TURNO"], row)
                        for _ in range(1000):
                            line = text.readline()
                            if not line:
                                break
                            row = dict(zip(columns, next(csv.reader([line], delimiter=";"))))
                            examples.setdefault(row["NR_TURNO"], row)
                            if len(examples) == 2:
                                break
                        entry["ejemplos_por_turno_muestra_acotada"] = examples
            result["miembros"].append(entry)
    result["bytes_descargados_sondeo"] = remote.downloaded
    return name, result


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        results = dict(pool.map(probe, URLS.items()))
    output = pathlib.Path(__file__).with_name("sondeo_tse.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
