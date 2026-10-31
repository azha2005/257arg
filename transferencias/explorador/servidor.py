"""Explorador de sankeys: elegí dos elecciones cualesquiera y se estima la matriz de transferencias al momento.
    python transferencias/explorador/servidor.py            # abre http://127.0.0.1:8790 en el navegador
    python transferencias/explorador/servidor.py --sin-abrir
Un cálculo por vez y con prioridad baja (la CPU no se recalienta); cada par queda guardado en cache/pares/."""
import os, sys, json, threading, traceback, webbrowser, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import datos, motor                                     # noqa: E402

PUERTO = int(os.environ.get("PUERTO", 8790))
LOCK = threading.Lock()
_cat = None


def prioridad_baja():
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)   # BELOW_NORMAL
    else:
        os.nice(10)


def catalogo():
    global _cat
    if _cat is None:
        _cat = dict(elecciones=datos.catalogo(), provincias=datos.PROVINCIAS)
    return _cat


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        sys.stderr.write("%s\n" % (fmt % a))

    def enviar(self, code, cuerpo, tipo="application/json; charset=utf-8"):
        b = cuerpo if isinstance(cuerpo, bytes) else json.dumps(cuerpo, ensure_ascii=False).encode("utf8")
        self.send_response(code); self.send_header("Content-Type", tipo); self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                self.enviar(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
            elif u.path == "/api/catalogo":
                self.enviar(200, catalogo())
            elif u.path == "/api/sankey":
                o, d = q["o"][0], q["d"][0]
                with LOCK:
                    r = motor.calcular(o, d, rapido=q.get("rapido", ["0"])[0] == "1")
                self.enviar(200, r)
            else:
                self.enviar(404, dict(error="no existe"))
        except Exception as e:
            traceback.print_exc()
            self.enviar(400, dict(error="%s: %s" % (type(e).__name__, e)))


def main():
    prioridad_baja()
    threading.Thread(target=lambda: (datos.master(), catalogo()), daemon=True).start()   # precarga
    srv = ThreadingHTTPServer(("127.0.0.1", PUERTO), H)
    url = "http://127.0.0.1:%d/" % PUERTO
    print("Explorador de sankeys en", url, flush=True)
    if "--sin-abrir" not in sys.argv:
        webbrowser.open(url)
    srv.serve_forever()


if __name__ == "__main__":
    main()
