"""El explorador como app de Streamlit (para Streamlit Community Cloud, que corre Python gratis).
    streamlit run transferencias/explorador/streamlit_app.py
Los selectores y el cálculo van en Python (los mismos datos.py y motor.py que servidor.py); el sankey lo dibuja
index.html en modo incrustado (window.EMBED), así la página local y la app dibujan exactamente lo mismo."""
import os, sys, json, threading

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import streamlit as st                                    # noqa: E402
import streamlit.components.v1 as components               # noqa: E402
import datos, motor                                       # noqa: E402

st.set_page_config(page_title="Transferencias de votos", page_icon="🗳️", layout="wide")


@st.cache_resource(show_spinner="Cargando el catálogo de elecciones…")
def catalogo():
    datos.master()
    return dict(elecciones=datos.catalogo(), provincias=datos.PROVINCIAS)


@st.cache_resource
def candado():
    return threading.Lock()          # un cálculo por vez, como servidor.py


@st.cache_data(max_entries=200, show_spinner=False)
def sankey(o, d, rapido):
    with candado():
        return motor.calcular(o, d, rapido=rapido)


CAT = catalogo()
ELEC = sorted(CAT["elecciones"], key=lambda e: (e["grupo"], e["anio"], e["nombre"]))
IDS = [e["id"] for e in ELEC]
POR_ID = {e["id"]: e for e in ELEC}
etiqueta = lambda i: "%s%s   — %s" % (POR_ID[i]["nombre"], " [circuitos]" if POR_ID[i].get("nivel") == "circuito" else "", POR_ID[i]["grupo"])

qp = st.query_params
if "o" not in st.session_state:
    st.session_state.o = qp.get("o") if qp.get("o") in POR_ID else "pkl:2023p"
    st.session_state.d = qp.get("d") if qp.get("d") in POR_ID else "pkl:2023b"


def invertir():
    st.session_state.o, st.session_state.d = st.session_state.d, st.session_state.o


st.markdown(
    "<style>.block-container{padding-top:2rem!important;padding-bottom:1rem!important;"
    "max-width:calc(1304px + 10rem)!important;margin-inline:auto}"   # el mismo ancho que el contenido de index.html
    "h1{letter-spacing:-0.04em;font-size:1.728rem!important;padding-bottom:0.25rem!important}"
    "[data-testid=stCaptionContainer]{max-width:75ch}</style>", unsafe_allow_html=True)
st.title("Explorador de transferencias de votos")
st.caption("Elegí dos elecciones argentinas cualesquiera (%d). La matriz se estima en el momento con inferencia ecológica "
           "RxC (E. Calvo): una matriz por provincia encogida hacia la nacional. Es la estimación puntual, sin intervalos; "
           "un par nuevo puede tardar hasta un minuto y después queda guardado. Escribí en la lista para filtrar." % len(IDS))
c1, c2, c3 = st.columns([10, 1, 10], vertical_alignment="bottom")
c1.selectbox("Origen", IDS, key="o", format_func=etiqueta)
c2.button("⇄", on_click=invertir, help="Invertir origen y destino")
c3.selectbox("Destino", IDS, key="d", format_func=etiqueta)
with st.container(horizontal=True, vertical_alignment="center", gap="medium"):
    ir = st.button("Calcular sankey", type="primary")
    rapido = st.checkbox("Rápido (sin validación cruzada)")

o, d = st.session_state.o, st.session_state.d
if ir or (qp.get("o") == o and qp.get("d") == d):
    st.query_params.update(o=o, d=d)
    if o == d:
        st.warning("Origen y destino son la misma elección.")
        st.stop()
    try:
        with st.spinner("Calculando %s → %s…" % (POR_ID[o]["nombre"], POR_ID[d]["nombre"])):
            R = sankey(o, d, rapido)
    except Exception as e:
        st.error("No se pudo calcular: %s" % e)
        st.stop()
    emb = json.dumps(dict(cat=CAT, r=R), ensure_ascii=False).replace("</", "<\\/")
    html = open(os.path.join(HERE, "index.html"), encoding="utf8").read()
    html = html.replace("<script>\nconst W=", "<script>window.EMBED=%s;</script>\n<script>\nconst W=" % emb, 1)
    components.html(html, height=980 + 18 * len(R["notas"]), scrolling=True)   # el sankey a 900 px y el panel con provincias plegadas
else:
    st.info("Elegí origen y destino y tocá «Calcular sankey». La vista por provincia, «sin No votó» y las descargas "
            "aparecen arriba del dibujo.")
st.caption("Código y datos: [github.com/azha2005/257arg](https://github.com/azha2005/257arg), `transferencias/explorador/`. "
           "Marcas: * fila no identificada, † fila cerca del promedio; aviso rojo si la matriz es poco informativa.")
