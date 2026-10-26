"""Tablas por provincia (diputados) del articulo de Wikipedia «Elecciones legislativas de Argentina de 2001» -> wiki_prov.json"""
import re, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(HERE, "w2001.txt"), encoding="utf8").read()
i = t.index("== Resultados por provincia ==")
seg = t[i:]
secs = re.split(r'\|-\s*id="([^"]+)"', seg)
out = {}
for k in range(1, len(secs), 2):
    pid, body = secs[k], secs[k + 1]
    if pid.startswith("Sen"):
        continue
    # solo la tabla de diputados: hasta el id del senado
    rows, pos = [], {}
    lines = body.split("\n")
    n = len(lines)
    j = 0
    while j < n:
        l = lines[j]
        m = re.match(r"\|\s*align=left[^|]*\|(.*)$", l)
        if m:
            name = re.sub(r"\{\{Lista desplegable.*", "", m.group(1))
            name = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", name).strip()
            # los nombres con lista desplegable ocupan varias lineas: avanzar hasta la linea de votos
            jj = j + 1
            while jj < n and not re.match(r"^\|\s*[\d\.]+\s*$", lines[jj]):
                if lines[jj].startswith("|-"): break
                jj += 1
            if jj < n and re.match(r"^\|\s*[\d\.]+\s*$", lines[jj]):
                v = int(lines[jj].strip("| ").replace(".", ""))
                nm = name.strip() or "?"
                if re.match(r"(Votos positivos|Votos en blanco|Votos nulos|Votos anulados|Electores registrados|Participaci)", nm):
                    pos[nm.split()[0] + " " + (nm.split()[1] if len(nm.split()) > 1 else "")] = v
                else:
                    rows.append([nm, v])
            j = jj
        j += 1
    out[pid] = dict(rows=rows, resto=pos)
json.dump(out, open(os.path.join(HERE, "wiki_prov.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
for p, d in out.items():
    print(p, len(d["rows"]), d["resto"])
