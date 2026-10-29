"""Baja el wikitext de los artículos de la Wikipedia en español usados por los atlas 1946-1973."""
import json, os, time, urllib.parse, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
ART = {"1946": "Elecciones presidenciales de Argentina de 1946",
       "1948": "Elecciones legislativas de Argentina de 1948",
       "1948c": "Elecciones de convencionales constituyentes de Argentina de 1948",
       "1951": "Elecciones presidenciales de Argentina de 1951",
       "1954": "Elecciones legislativas de Argentina de 1954",
       "1973": "Elecciones presidenciales de Argentina de marzo de 1973",
       "1973s": "Elecciones presidenciales de Argentina de septiembre de 1973"}
UA = {"User-Agent": "dataelecc-atlas/1.0 (bttfjc@gmail.com)"}
for k, a in ART.items():
    dst = os.path.join(H, "wiki", "w%s.txt" % k)
    if os.path.exists(dst): continue
    q = urllib.parse.urlencode(dict(action="parse", page=a, prop="wikitext", format="json", redirects=1))
    for t in range(6):
        try:
            j = json.load(urllib.request.urlopen(urllib.request.Request("https://es.wikipedia.org/w/api.php?" + q, headers=UA), timeout=60)); break
        except Exception as e:
            print(k, e); time.sleep(5 * (t + 1))
    if "error" in j: print(k, j["error"]); continue
    open(dst, "w", encoding="utf8").write(j["parse"]["wikitext"]["*"]); print(k, j["parse"]["title"], len(j["parse"]["wikitext"]["*"]))
    time.sleep(1)
