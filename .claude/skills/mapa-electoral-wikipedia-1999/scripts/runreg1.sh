#!/bin/bash
# Registro de UN inset en una instancia aislada de Edge (lanzar varios en paralelo: cada busqueda usa un solo hilo).
#   runreg1.sh <atlas.html> <ref.png> <inset> <salida.json>      inset: tuc|sj|mza|res|amba|caba
# Ejemplo (6 a la vez):  for n in tuc sj mza res amba caba; do ./runreg1.sh atlas.html 1999.png $n reg_$n.json & done; wait
HTML="$1"; REF="$2"; N="$3"; OUT="$4"
D="$(cd "$(dirname "$0")" && pwd)"; TMP="$(mktemp -d)"
python3 - "$HTML" "$REF" "$N" "$D/regsearch.js" "$TMP/run.html" <<'PY'
import sys, os, pathlib
html, ref, n, js, out = sys.argv[1:6]
s = open(html, encoding="utf8").read()
refurl = pathlib.Path(os.path.abspath(ref)).as_uri()
code = open(js, encoding="utf8").read()
s = s.replace("</body>", "<script>window.__REF=%r;window.__WANT=%r;</script><script>%s</script></body>" % (refurl, n, code), 1)
open(out, "w", encoding="utf8").write(s)
PY
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
"$EDGE" --headless --disable-gpu --allow-file-access-from-files --user-data-dir="$(cygpath -w "$TMP/prof")" \
  --virtual-time-budget=900000 --window-size=1920,1649 --dump-dom "file:///$(cygpath -m "$TMP/run.html")#bare" 2>/dev/null \
  | grep -o '<pre id="res">.*</pre>' > "$OUT"
rm -rf "$TMP"
