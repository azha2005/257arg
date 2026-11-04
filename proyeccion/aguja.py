"""Aguja de la noche electoral: repeticion de una eleccion pasada con un orden de llegada simulado.
    python proyeccion/aguja.py 2023p 2023b --orden geo          # balotaje 2023 desde la 1.a vuelta
    python proyeccion/aguja.py 2019p 2023p --circuito --orden geo
    python proyeccion/aguja.py 2023p 2023b --cobertura          # solo mide la cobertura de la banda (varios ordenes)
En cada paso (de 0,1 % a 100 % de las mesas):
  - escrutado: % de cada fuerza en lo contado (linea llena);
  - proyeccion: D sin benchmarking de backtest.py, con banda nominal del 95 % = bootstrap de circuitos de todo
    el estimador (incluidas matrices locales y residuos) mas error sistematico por llegada (SIS),
    que se achica a medida que avanza el conteo; --cobertura mide si la banda contiene el resultado real;
  - probabilidad de que cada fuerza termine primera (proporcion de remuestras);
  - evolucion esperada del escrutado (linea punteada): las mesas que faltan se ordenan por la velocidad de su
    seccion (fraccion ya contada, encogida hacia la del distrito) y se acumulan con su voto proyectado. No es la
    ilustracion del Estadao: usa lo que ya se vio de la llegada.
Salida: proyeccion/aguja_<origen>_<destino>_<orden>.html (autocontenido) y .json."""
import os, sys, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest as bt

ORDEN = sys.argv[sys.argv.index("--orden") + 1] if "--orden" in sys.argv else "geo"
BOOT = 200
FACTOR = 1.0
MODELO = "D_sin_ajuste"  # validacion_20261028: universo completo; bootstrap de todo el estimador
# Error sistematico por el orden de llegada (el bootstrap solo mide el azar de las mesas contadas): desvio
# a*(1-f)*f^-b, con f = fraccion de mesas contadas. Ajustado el 27-oct-2026 con el p95 de |error| de D en los ordenes
# geo y geo_circ de backtest.py (2023 y 2015 mesa a mesa; 2019 -> 2023 por circuito). Sin el, la banda del 95 %
# contiene el resultado el 95 % de las veces con mesas al azar pero 16-67 % con los ordenes sesgados.
SIS = {"mesa": (0.523, 0.203), "circuito": (0.603, 0.316)}
SIS_PISO = 1.8  # entre años: calibrado solo con 2019->2023; validacion separada en 2025


def sistematico(f):
    a, b = SIS["circuito" if bt.CIRC else "mesa"]
    base = a * (1 - f) * f ** -b
    return max(base, SIS_PISO * (1 - f)) if bt.CIRC else base
NOMBRES = {"LA LIBERTAD AVANZA": "La Libertad Avanza", "UNION POR LA PATRIA": "Unión por la Patria",
           "JUNTOS POR EL CAMBIO": "Juntos por el Cambio", "HACEMOS POR NUESTRO PAIS": "Hacemos por Nuestro País",
           "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "Frente de Izquierda", "FRENTE DE TODOS": "Frente de Todos",
           "CAMBIEMOS": "Cambiemos", "ALIANZA CAMBIEMOS": "Cambiemos", "FRENTE PARA LA VICTORIA": "Frente para la Victoria",
           "ALIANZA FRENTE PARA LA VICTORIA": "Frente para la Victoria", "ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA)": "UNA",
           "OTRAS LISTAS": "Otras listas"}
# Colores de la paleta presidencial de los atlas (AGENTS.md)
COLORES = {"La Libertad Avanza": "#6c4c98", "Unión por la Patria": "#009ce4", "Juntos por el Cambio": "#fcbc00",
           "Hacemos por Nuestro País": "#283084", "Frente de Izquierda": "#e10019", "Frente de Todos": "#2ea3ff",
           "Cambiemos": "#f4ce00", "Frente para la Victoria": "#50ade6", "UNA": "#231f20"}
STEPS = np.unique(np.r_[np.geomspace(0.001, 0.05, 25), np.linspace(0.06, 1, 48)])


def national_boot(st, cnt, F, rng, nboot):
    """% de cada fuerza (sobre positivos) en el total proyectado, para cada remuestra de circuitos contados."""
    if MODELO == "D_sin_ajuste":
        seen = np.unique(st["circ"][cnt])
        out = []
        for b in range(nboot + 1):
            weights = None
            if b:
                count = np.bincount(rng.choice(seen, len(seen)), minlength=st["circ"].max() + 1)
                weights = count[st["circ"]]
            V = bt.project_BC(st, cnt, True, "F_tam", bench=False, fitweights=weights)
            v = V.sum(0)[st["pos"]]
            out.append(100 * v / v.sum())
        return np.array(out)
    circ, e, Y = st["circ"], st["e"], st["Y"]
    ncirc = circ.max() + 1
    # estadisticos de los circuitos solo con sus mesas contadas
    W = F[cnt] * e[cnt, None]
    Ac = np.zeros((ncirc, F.shape[1], F.shape[1]))
    Cc = np.zeros((ncirc, F.shape[1], Y.shape[1]))
    np.add.at(Ac, circ[cnt], W[:, :, None] * F[cnt][:, None, :])
    np.add.at(Cc, circ[cnt], W[:, :, None] * Y[cnt][:, None, :])
    seen = np.unique(circ[cnt])
    kx = st["X"].shape[1]
    counted = (Y[cnt] * e[cnt, None]).sum(0)
    Fun = (F[~cnt] * e[~cnt, None]).sum(0)                      # el total que falta es lineal en F
    pos = st["pos"]
    out = []
    for b in range(nboot + 1):
        mult = np.bincount(rng.choice(seen, len(seen)), minlength=ncirc) if b else np.bincount(seen, minlength=ncirc)
        A = np.tensordot(mult, Ac, 1)
        C = np.tensordot(mult, Cc, 1)
        pen = np.zeros(len(A))
        pen[kx:] = bt.N0S * np.diag(A)[kx:] / max(cnt.sum(), 1)
        G = np.linalg.solve(A + np.diag(pen) + 1e-9 * np.eye(len(A)), C)
        tot = counted + Fun @ G
        out.append(100 * tot[pos] / tot[pos].sum())
    return np.array(out)                                          # fila 0 = estimacion puntual


def expected_path(st, cnt, V, grid_n):
    """Escrutado esperado de aca a 100 %: mesas que faltan, primero las de secciones mas avanzadas."""
    sec, dist, e = st["sec"], st["dist"], st["e"]
    ns, nd = sec.max() + 1, dist.max() + 1
    done_s = np.bincount(sec, weights=cnt, minlength=ns)
    all_s = np.bincount(sec, minlength=ns)
    done_d = np.bincount(dist, weights=cnt, minlength=nd)
    rate_d = done_d / np.bincount(dist, minlength=nd)
    k = 10.0                                                      # mesas de peso de la tasa del distrito
    rate_s = (done_s + k * rate_d[st["sec_dist"]]) / (all_s + k)
    un = np.where(~cnt)[0]
    order = un[np.argsort(-rate_s[sec[un]], kind="stable")]
    cum = np.cumsum(V[order], axis=0) + V[cnt].sum(0)
    idx = np.unique(np.linspace(0, len(order) - 1, grid_n).astype(int))
    pos = st["pos"]
    x = (cnt.sum() + idx + 1) / len(e)
    shares = 100 * cum[idx][:, pos] / cum[idx][:, pos].sum(1, keepdims=True)
    return x, shares


def run(st, kind, seed, nboot=BOOT, path=True):
    rng = np.random.default_rng(seed)
    n = len(st["e"])
    o = bt.order(st, kind, rng)
    F = np.column_stack([st["X"], st["F_tam"]])                  # modelo nacional de D
    real = 100 * st["Vd"].sum(0)[st["pos"]] / st["Vd"].sum(0)[st["pos"]].sum()
    steps = []
    for f in STEPS:
        cnt = np.zeros(n, bool)
        cnt[o[:max(1, int(round(f * n)))]] = True
        Vc = st["Vd"][cnt].sum(0)
        crudo = 100 * Vc[st["pos"]] / Vc[st["pos"]].sum()
        if f < 1:
            boot = national_boot(st, cnt, F, rng, nboot)
            point = boot[0]
            sis = sistematico(cnt.mean())
            noise = rng.normal(0, sis, boot[1:].shape)
            noise -= noise.mean(1, keepdims=True)
            noise *= np.sqrt(noise.shape[1] / max(noise.shape[1] - 1, 1))
            draws = point + FACTOR * (boot[1:] - boot[1:].mean(0) + noise)
            draws = np.maximum(draws, 0)
            draws = 100 * draws / draws.sum(1, keepdims=True)
            lo, hi = np.percentile(draws, [2.5, 97.5], axis=0)
            prob = np.bincount(draws.argmax(1), minlength=len(point)) / len(draws)
        else:
            point = lo = hi = crudo
            prob = (crudo == crudo.max()).astype(float)
        rec = dict(x=float(cnt.mean()), crudo=crudo.round(3).tolist(), proy=point.round(3).tolist(),
                   lo=lo.round(3).tolist(), hi=hi.round(3).tolist(), prob=prob.round(3).tolist())
        if path and f < 1:
            V = bt.project_BC(st, cnt, True, "F_tam", bench=False)
            px, ps = expected_path(st, cnt, V, 40)
            rec["camino_x"] = px.round(4).tolist()
            rec["camino"] = ps.round(3).tolist()
        steps.append(rec)
    return steps, real


def cobertura(st):
    """Fraccion de pasos en que la banda del 95 % contiene el resultado real, por orden y tramo de escrutinio."""
    rows = []
    for kind in ("azar", "geo", "geo_circ", "sesgo"):
        for seed in range(6):
            steps, real = run(st, kind, 100 + seed, nboot=100, path=False)
            for s in steps[:-1]:
                lo, hi = np.array(s["lo"]), np.array(s["hi"])
                p = np.array(s["proy"])
                j = int(np.argmax(real))
                rows.append(dict(orden=kind, x=s["x"], dentro=bool(lo[j] <= real[j] <= hi[j]),
                                 z=abs(p[j] - real[j]) / max((hi[j] - lo[j]) / 3.92, 1e-9)))
    df = pd.DataFrame(rows)
    df["tramo"] = pd.cut(df.x, [0, .01, .05, .25, 1], labels=["<1 %", "1-5 %", "5-25 %", ">25 %"])
    return df


def html(steps, real, names, title, colors):
    data = json.dumps(dict(steps=steps, real=list(map(float, real)), names=names, colors=colors, title=title), ensure_ascii=False)
    return TEMPLATE.replace("__DATA__", data).replace("__TITLE__", title)


TEMPLATE = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#fafaf8;--card:#fff;--ink:#1d1d1b;--mute:#6b6b66;--line:#e4e2dc}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--ink:#ecebe6;--mute:#a3a29b;--line:#34332f}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:960px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:4px 0 2px}.sub{color:var(--mute);margin:0 0 14px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.cand{font-weight:600}.big{font-size:38px;font-weight:700;letter-spacing:-.5px}.big small{font-size:18px;color:var(--mute)}
.mute{color:var(--mute);font-size:13px}.band{font-weight:600}
.bar{height:6px;border-radius:3px;background:var(--line);margin-top:6px;overflow:hidden}.bar i{display:block;height:100%}
svg{width:100%;height:auto;display:block}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px}
input[type=range]{width:100%}
.leg{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--mute);margin:4px 6px}
</style></head><body><main>
<h1>__TITLE__</h1>
<p class="sub" id="sub"></p>
<div class="cards" id="cards"></div>
<div class="chart">
<div class="leg"><span>— escrutado</span><span>─ (fina) proyección en cada momento</span><span>┄ escrutado esperado</span><span>▮ proyección (banda nominal del 95 %)</span><span>· · resultado real</span></div>
<svg id="g" viewBox="0 0 900 420"></svg>
<input type="range" id="t" min="0" value="0">
<p class="mute" id="lbl"></p>
</div>
<p class="mute">Repetición de una elección ya terminada con un orden de llegada simulado; la línea punteada es el
escrutado que se espera si las mesas que faltan llegan primero en las secciones más avanzadas. Proyección: D sin ajuste forzoso del total.
(<code>proyeccion/backtest.py</code>).</p>
<p class="mute">Las bandas son condicionales al modelo y no garantizan cobertura ante selección por resultado.
En la prueba separada de 2025 el escenario extremo «sesgo» siguió mostrando subcobertura.
Las frecuencias de las simulaciones no son probabilidades calibradas de certeza electoral.</p>
</main>
<script>
const D=__DATA__;const S=D.steps;const t=document.getElementById('t');t.max=S.length-1;
const W=900,H=420,L=46,R=240,T=14,B=34;
const allv=S.flatMap(s=>s.crudo.concat(s.lo,s.hi));
let y0=Math.floor(Math.max(0,Math.min(...allv.filter(v=>v>3))-3)),y1=Math.ceil(Math.min(100,Math.max(...allv)+3));
const X=x=>L+(W-L-R)*x, Y=v=>T+(H-T-B)*(1-(v-y0)/(y1-y0));
const fmt=v=>v.toFixed(2).replace('.',',');
function draw(k){
  const s=S[k];let h='';
  for(let v=Math.ceil(y0/5)*5;v<=y1;v+=5)h+=`<line x1="${L}" x2="${W-R}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--line)"/><text x="${L-6}" y="${Y(v)+4}" text-anchor="end" font-size="12" fill="var(--mute)">${v}%</text>`;
  for(let p=0;p<=100;p+=20)h+=`<text x="${X(p/100)}" y="${H-12}" text-anchor="middle" font-size="12" fill="var(--mute)">${p}%</text>`;
  D.names.forEach((n,j)=>{
    const c=D.colors[j];
    const pts=S.slice(0,k+1).map(q=>`${X(q.x)},${Y(q.crudo[j])}`).join(' ');
    h+=`<polyline points="${pts}" fill="none" stroke="${c}" stroke-width="2.2"/>`;
    const pp=S.slice(0,k+1).map(q=>`${X(q.x)},${Y(q.proy[j])}`).join(' ');
    h+=`<polyline points="${pp}" fill="none" stroke="${c}" stroke-width="1" opacity=".55"/>`;
    if(s.camino){const cp=[`${X(s.x)},${Y(s.crudo[j])}`].concat(s.camino_x.map((x,i)=>`${X(x)},${Y(s.camino[i][j])}`)).join(' ');
      h+=`<polyline points="${cp}" fill="none" stroke="${c}" stroke-width="1.8" stroke-dasharray="4 4" opacity=".8"/>`;}
    h+=`<rect x="${X(1)-3}" y="${Y(s.hi[j])}" width="6" height="${Math.max(2,Y(s.lo[j])-Y(s.hi[j]))}" fill="${c}" opacity=".45"/>`;
    h+=`<circle cx="${X(1)}" cy="${Y(s.proy[j])}" r="4.5" fill="${c}"/>`;
    h+=`<line x1="${X(1)-10}" x2="${X(1)+10}" y1="${Y(D.real[j])}" y2="${Y(D.real[j])}" stroke="var(--ink)" stroke-dasharray="2 2"/>`;
  });
  // rotulos sin pisarse: se ordenan por altura y se separan al menos 17 px
  const lab=D.names.map((n,j)=>({j,y:Y(s.proy[j])+4})).sort((a,b)=>a.y-b.y);
  for(let i=1;i<lab.length;i++)if(lab[i].y-lab[i-1].y<17)lab[i].y=lab[i-1].y+17;
  lab.forEach(({j,y})=>{h+=`<text x="${X(1)+14}" y="${y}" font-size="13" font-weight="600" fill="var(--ink)">${D.names[j]} ${fmt(s.proy[j])}%</text>`;});
  document.getElementById('g').innerHTML=h;
  const ord=D.names.map((n,j)=>j).sort((a,b)=>s.proy[b]-s.proy[a]);
  document.getElementById('cards').innerHTML=ord.map(j=>[D.names[j],j]).map(([n,j])=>`<div class="card"><div class="cand" style="color:${D.colors[j]}">${n}</div>
   <div class="big">${fmt(s.proy[j])}<small>%</small></div><div class="mute">proyección del resultado final</div>
   <div class="band">95 %: ${fmt(s.lo[j])} – ${fmt(s.hi[j])}</div><div class="mute">escrutado ahora: ${fmt(s.crudo[j])} % · real: ${fmt(D.real[j])} %</div>
   <div class="mute">primer puesto en las simulaciones: ${(100*s.prob[j]).toFixed(0)} %</div><div class="bar"><i style="width:${100*s.prob[j]}%;background:${D.colors[j]}"></i></div></div>`).join('');
  document.getElementById('lbl').textContent=`Mesas escrutadas: ${(100*s.x).toFixed(1).replace('.',',')} %`;
}
t.oninput=()=>draw(+t.value);
const start=S.findIndex(s=>s.x>=0.01);t.value=start<0?0:start;draw(+t.value);
document.getElementById('sub').textContent=D.sub||'';
</script></body></html>"""


def main():
    st, info, dcols = bt.state()
    if "--cobertura" in sys.argv:
        df = cobertura(st)
        tab = df.groupby(["orden", "tramo"], observed=True).agg(cobertura=("dentro", "mean"), z_p95=("z", lambda s: s.quantile(.95))).round(3)
        out = os.path.join(HERE, "cobertura_%s_%s%s.csv" % (bt.Y0, bt.Y1, "_circuito" if bt.CIRC else ""))
        tab.to_csv(out)
        print(tab.to_string())
        return
    steps, real = run(st, ORDEN, 2027)
    names = [NOMBRES.get(dcols[p], dcols[p].title()) for p in st["pos"]]
    keep = [j for j in range(len(names)) if real[j] >= 3 and names[j] != "Otras listas"]
    for s in steps:
        for k in ("crudo", "proy", "lo", "hi", "prob"):
            s[k] = [s[k][j] for j in keep]
        if "camino" in s:
            s["camino"] = [[r[j] for j in keep] for r in s["camino"]]
    names = [names[j] for j in keep]
    real = [real[j] for j in keep]
    palette = ["#6c4c98", "#009ce4", "#f4ce00", "#2f3b81", "#e10019", "#ff6600"]
    colors = [COLORES.get(n, palette[i % len(palette)]) for i, n in enumerate(names)]
    tag = "%s_%s_%s" % (bt.Y0, bt.Y1, ORDEN)
    title = "Aguja: %s → %s (orden «%s»)" % (bt.Y0, bt.Y1, ORDEN)
    json.dump(dict(steps=steps, real=real, names=names), open(os.path.join(HERE, "aguja_%s.json" % tag), "w", encoding="utf-8"))
    open(os.path.join(HERE, "aguja_%s.html" % tag), "w", encoding="utf-8").write(html(steps, real, names, title, colors))
    print("aguja", tag, "real", np.round(real, 2))


if __name__ == "__main__":
    main()
