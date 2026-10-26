"""Lee la tabla provincial del docx (la línea alternativa) y la valida. -> tabla_1916fic.json"""
import json, os, docx
HERE = os.path.dirname(os.path.abspath(__file__))
t = docx.Document(os.path.join(HERE, "lore_1916.docx")).tables[0]
rows = [[c.text.strip() for c in r.cells] for r in t.rows][2:]


def n(s):
    return int(s.replace(".", "")) if s.strip() else 0


COLS = dict(EL=1, UCR=2, ELU=4, PDP=5, ELP=7, PS=8, ELS=10, CC=11, ELC=13, RAD=14, ELR=16, BLA=17, VOT=19, REG=21)
T = {}
for r in rows:
    d = {k: n(r[i]) for k, i in COLS.items()}
    T[r[0]] = d
tot = T.pop("Total")
# Jujuy trae «8..993»: se lee 8.993 (61,94 % de 14.519)
bad = []
for p, d in T.items():
    pos = d["UCR"] + d["PDP"] + d["PS"] + d["CC"] + d["RAD"]
    if pos + d["BLA"] != d["VOT"]:
        bad.append((p, pos + d["BLA"], d["VOT"]))
    if d["ELU"] + d["ELP"] + d["ELS"] + d["ELC"] + d["ELR"] != d["EL"]:
        bad.append((p, "electores"))
print("filas que no cierran:", bad)
for k in COLS:
    s = sum(d[k] for d in T.values())
    print(k, s, tot[k], "OK" if s == tot[k] else "DIFIERE %+d" % (s - tot[k]))
json.dump(dict(prov=T, total=tot), open(os.path.join(HERE, "tabla_1916fic.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
