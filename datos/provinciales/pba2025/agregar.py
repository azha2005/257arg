"""Provinciales bonaerenses del 7-sep-2025 por mesa (provisorio; base de graficarpba, a pedido) -> por circuito.
    python datos/provinciales/pba2025/agregar.py
Cargo legislativo unificado: senadores en las secciones 1.a, 4.a, 5.a y 7.a, diputados en 2.a, 3.a, 6.a y 8.a (cada mesa vota uno solo).
Codigos de la base (deducidos y verificados contra la DINE de octubre):
  mesa_key / codigo_mesa = '02' + partido (3, numeracion de la DINE) + mesa (5) + X (argentinos) o E (extranjeros, solo votan provinciales)
  circuito_codigo = '02' + partido (3) + circuito (5, con letra si esta subdividido: 0655A); seccion_* es el partido, municipio_* la localidad
  code = numero de lista provincial; census = electores de la mesa; totalVotos = votantes (afirmativos + blancos + recurridos + impugnados + comando)
  La base no trae nulos (columna en 0) ni electores/sobres fiables (electores vale 0 en 7.694 mesas): no se usan.
Salidas: circuitos.csv (ancho, una fila por circuito; mesas X y E por separado) y transferencias/circ_2025s.pkl
(solo mesas X con votos, mismo formato que agregar_circuitos.py; agrupacion_id = nombre de la lista)."""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
FILES = {"senadores": "resultados_senadores_provinciales.csv", "diputados": "resultados_diputados_provinciales.csv"}
COLS = ["mesa_key", "circuito_codigo", "seccion_codigo", "seccion_nombre", "seccion_electoral_nombre", "name", "votos",
        "census", "totalVotos", "blancos", "recurridos", "impugnados", "comando"]
NUM = ["votos", "census", "totalVotos", "blancos", "recurridos", "impugnados", "comando"]

d = pd.concat([pd.read_csv(os.path.join(HERE, f), dtype=str, usecols=COLS).assign(cargo=c) for c, f in FILES.items()])
for c in NUM:
    d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
assert not d.duplicated(["mesa_key", "name"]).any()
d["tipo"] = d.mesa_key.str[-1]
d["seccion_id"] = d.circuito_codigo.str[2:5].astype(int)
d["circuito"] = d.circuito_codigo.str[5:].str.lstrip("0").replace("", "0")
m = d.drop_duplicates("mesa_key")
key = ["seccion_id", "circuito"]

# --- circuitos.csv: votos por lista, electores y votantes, con las mesas de extranjeros aparte
wide = d.pivot_table(index=key + ["tipo"], columns="name", values="votos", aggfunc="sum", fill_value=0)
tot = m.groupby(key + ["tipo"]).agg(electores=("census", "sum"), votantes=("totalVotos", "sum"), blancos=("blancos", "sum"),
                                    recurridos=("recurridos", "sum"), impugnados=("impugnados", "sum"), comando=("comando", "sum"),
                                    mesas=("mesa_key", "size"), mesas_sin_votos=("totalVotos", lambda s: int((s == 0).sum())))
info = m.groupby(key).agg(partido=("seccion_nombre", "first"), seccion_electoral=("seccion_electoral_nombre", "first"),
                          cargo=("cargo", "first"))
out = tot.join(wide).reset_index().merge(info.reset_index(), on=key)
out.to_csv(os.path.join(HERE, "circuitos.csv"), index=False, encoding="utf-8-sig")

# --- circ_2025s.pkl para transferencias/estimar.py: solo mesas de argentinos (X) escrutadas
x = d[(d.tipo == "X") & (d.mesa_key.isin(m.loc[m.totalVotos > 0, "mesa_key"]))]
mx = x.drop_duplicates("mesa_key")
pos = x.groupby(key + ["name"]).votos.sum().reset_index().rename(columns={"name": "agrupacion_id", "votos": "v"}).assign(votos_tipo="POSITIVO")
otros = [mx.groupby(key)[c].sum().reset_index().rename(columns={c: "v"}).assign(agrupacion_id="0000", votos_tipo=t)
         for c, t in [("blancos", "EN BLANCO"), ("recurridos", "RECURRIDO"), ("impugnados", "IMPUGNADO"), ("comando", "COMANDO")]]
votes = pd.concat([pos] + otros).assign(distrito_id="02")
votes = votes[["distrito_id", "seccion_id", "circuito", "agrupacion_id", "votos_tipo", "v"]]
elect = mx.assign(distrito_id="02").groupby(["distrito_id"] + key).census.sum().rename("e")
pd.to_pickle((votes, elect), os.path.join(ROOT, "transferencias", "circ_2025s.pkl"))

print("mesas", len(m), "(X %d, E %d, sin votos %d)" % ((m.tipo == "X").sum(), (m.tipo == "E").sum(), (m.totalVotos == 0).sum()))
print("circuitos", out[key].drop_duplicates().shape[0], "electores", int(m.census.sum()), "votantes", int(m.totalVotos.sum()))
print("pkl: circuitos", len(elect), "electores", int(elect.sum()), "votos", int(votes.v.sum()))
print(d.groupby("name").votos.sum().sort_values(ascending=False).astype(int).head(8).to_string())
