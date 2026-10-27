"""Sankey (el mismo sankey.py de los cruces argentinos) e informe del cruce presidencial brasileño 2026.
    python -X utf8 transferencias/brasil2026_presentar.py
Escribe sankey_brasil_2026p_2026b(.svg/.html), las versiones _votantes y _reducido y RESUMEN.md. Los PNG salen de brasil2026_revisar_html.py."""
import json

import pandas as pd

import sankey
from brasil2026_datos import OUT, RAW

NIVEL = {"uf": "UF", "intermedia": "región geográfica intermedia", "inmediata": "región geográfica inmediata"}


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def pc(x, d=1):
    return f"{x:.{d}f}".replace(".", ",") + " %"


def num(x, d=3):
    return f"{x:.{d}f}".replace(".", ",")


def estado(a):
    marcas = ["No identificada" if a["no_identificada"] else "Sensible" if a["sensible"] else ""]
    if a["borde"]:
        marcas.append("borde: " + ", ".join(a["borde"]))
    return "; ".join(m for m in marcas if m) or "Sin alerta por estos criterios"


def main():
    dump_sources = {k: json.loads((RAW/f"{k}.json").read_text(encoding="utf8")) for k in ["votos", "detalle"]}
    dump_sources["ibge"] = json.loads((RAW/"ibge"/"fuentes.json").read_text(encoding="utf8"))
    (OUT/"fuentes_manifest.json").write_text(json.dumps(dump_sources, ensure_ascii=False, indent=2), encoding="utf8")
    sankey.main("brasil2026p", "2026b")
    sankey.main("brasil2026p", "2026b", votantes=True)
    sankey.main("brasil2026p", "2026b", reducido=True)
    sankey.main("brasil2026p", "2026b", reducido=True, breve=True)
    ctl = json.loads((OUT/"control.json").read_text(encoding="utf8"))
    M = pd.read_csv(OUT/"matriz_votos.csv", index_col=0)
    pct = pd.read_csv(OUT/"matriz_pct.csv", index_col=0)
    iv = pd.read_csv(OUT/"intervalos.csv").set_index(["origen", "destino"])
    audit = {r: ctl["auditoria_extra"][r] for r in M.index}
    cov = pd.read_csv(OUT/"cobertura_por_uf.csv").set_index("uf")
    coverage = cov.electores_usados.sum()/cov.electores_2.sum()*100
    nivel, lam2 = ctl["nivel"], ctl["lambda_region"].get(ctl["nivel"])
    fz = ctl["fuera_de_muestra"]
    mejor_uf = 100*(1 - fz[nivel]["rmse"]/fz["UF"]["rmse"]) if nivel != "uf" else 0
    rows = ["# Brasil 2026: primera vuelta → balotaje", "",
            "Estimaciones ecológicas a partir de los votos y padrones por sección del TSE, no observaciones de cambios individuales de voto.", "",
            "[Abrir gráfico con selector de UF](sankey_brasil_2026p_2026b.html) | [PNG](sankey_brasil_2026p_2026b.png) | "
            "[Versión sin No votó](sankey_brasil_2026p_2026b_votantes.html) (misma estimación, sin la fila y la columna de abstención) | "
            "[Versión con No votó reducido](sankey_brasil_2026p_2026b_reducido.html) ([PNG](sankey_brasil_2026p_2026b_reducido.png); «No votó» dibujado a escala 1:4, cifras reales; [sin notas al pie](sankey_brasil_2026p_2026b_reducido_breve.html), [PNG](sankey_brasil_2026p_2026b_reducido_breve.png))", "",
            "## Cobertura y fuentes", "",
            f"- {fmt(ctl['secciones'])} secciones, {fmt(ctl['locales'])} locales y {fmt(ctl['municipios'])} municipios o localidades del exterior; 27 UF y exterior.",
            f"- {fmt(ctl['electores'])} electores del balotaje: **{pc(coverage, 2)}** del padrón publicado. No se extrapola el resto.",
            "- ZIP completos del TSE en `datos_oficiales/brasil2026/`, con SHA256, metadatos HTTP y diccionarios transcritos. Las sumas de electores, comparecimiento, abstención, blancos, nulos y cada candidato cierran exactamente con los JSON nacionales del TSE ([cotejo](cotejo_totales_tse.json)).",
            "- Particularidad: el CSV cuenta en QT_VOTOS_NOMINAIS los 5.246 votos del código 28 (Leonardo Araújo); el JSON los pasa a vnt. Se conserva la fila como opción observada.",
            "- El catálogo advierte 39 registros duplicados por transferencias temporarias; no se restaron arbitrariamente.",
            f"- Regiones geográficas del IBGE (2017): {ctl['regiones']['intermedia']} intermedias y {ctl['regiones']['inmediata']} inmediatas, contando el exterior como una. Correspondencia de códigos TSE→IBGE y casos especiales en `brasil2026_regiones.py` ([tabla](regiones_municipio.csv)).", "",
            "## Método", "",
            f"- Núcleo `rxc_calvo` del proyecto (mismo óptimo, calculado con estadísticos suficientes). Jerarquía: centro nacional → UF (penalización λ1 = {ctl['lambda']}) → **{NIVEL[nivel]}** (λ2 = {lam2}, hacia su UF).",
            "- λ1, λ2 y el nivel se eligen por validación cruzada con municipios enteros por fold (5 folds; el centro y las UF se recalculan sin el fold). Regla del proyecto: la penalización más fuerte dentro del 1 % del mínimo, y el nivel más simple dentro del 1 % del mejor.",
            "- Secciones comunes, instaladas, no anuladas, con cierre exacto entre votos y participación y padrón que cambia hasta 5 electores y 1 % (el origen se reescala al padrón de destino). Versión estricta con padrón idéntico como sensibilidad.",
            f"- Bootstrap: {ctl['bootstrap']} réplicas de locales dentro de cada UF; en cada una se recalculan el centro nacional, λ1 y λ2 (grillas completas). Nivel y marginales de origen fijos.",
            "- Sensibilidad por escala (local, municipio/zona, padrón idéntico): cada una elige su propia penalización y nivel por validación cruzada; con menos unidades, el ajuste de las secciones sobreajustaría.",
            "- Además del intervalo bootstrap, `intervalos.csv` trae el **rango entre especificaciones** (UF sola, el otro nivel regional, local, municipio/zona, padrón idéntico y Calvo): es la incertidumbre de modelo que el bootstrap no ve.", "",
            "### Validación cruzada (error por sección, puntos, sin No votó)", "",
            "| Nivel | Error con su λ |", "|---|---:|"]
    rows += [f"| {NIVEL[n]} | {num(e)} |" for n, e in ctl["error_cv_por_nivel"].items()]
    rows += ["", "### Fuera de muestra: predecir municipios que no entraron al ajuste", "",
             "3 repeticiones × 5 folds de municipios enteros; error ponderado por electores del balotaje, como en [fuera_de_muestra](../fuera_de_muestra/RESUMEN.md). "
             "«sin origen» = reparto medio de la UF; «media nacional» = reparto medio del país. Por UF en [fuera_de_muestra.csv](fuera_de_muestra.csv).", "",
             "| Modelo | Todas las categorías | Solo votantes |", "|---|---:|---:|"]
    rows += [f"| {m} | {num(v['rmse'])} | {num(v['rmse_votantes'])} |" for m, v in fz.items()]
    rows += ["", (f"La matriz por {NIVEL[nivel]} reduce el error fuera de muestra {pc(mejor_uf)} respecto de la de UF. Buena parte del error es ruido de cada sección (unos 300 electores), que ningún modelo puede bajar; "
                  "la mejora sobre la parte sistemática es mayor que ese porcentaje." if nivel != "uf" else "Las regiones no mejoran el ajuste fuera de muestra más de 1 %: queda la matriz por UF."), "",
             "## Matriz principal: porcentaje de cada origen", "",
             "| Origen | " + " | ".join(M.columns) + " | Auditoría |", "|---|" + "---:|"*len(M.columns) + "---|"]
    for r in M.index:
        rows.append("| " + r + " | " + " | ".join(pc(pct.loc[r, c]) for c in M.columns) + " | " + estado(audit[r]) + " |")
    rows += ["", "### Qué tan seguro es cada reparto hacia los finalistas", "",
             "Bootstrap 5–95 y rango entre especificaciones, en % de la fila.", "",
             "| Origen | → Lula | IC | Modelos | → Flávio | IC | Modelos |", "|---|---:|---|---|---:|---|---|"]
    for r in M.index:
        cells = []
        for c in ["Lula (PT)", "Flávio Bolsonaro (PL)"]:
            t, x = M.loc[r].sum(), iv.loc[(r, c)]
            cells += [pc(pct.loc[r, c]), f"{pc(100*x.p5/t)} – {pc(100*x.p95/t)}", f"{pc(100*x.min_modelos/t)} – {pc(100*x.max_modelos/t)}"]
        rows.append("| " + r + " | " + " | ".join(cells) + " |")
    borde = ctl["celdas_borde"]
    rows += ["", "## Auditoría", "",
             "- **No identificada**: diferencia principal/Calvo >30 puntos (o >20 si la fila pesa menos de 5 % del padrón), o >20 entre escalas o especificaciones. **Sensible**: alguna de esas diferencias >10 puntos. Detalle en [AUDITORIA.md](../AUDITORIA.md) y [auditoria_filas.csv](auditoria_filas.csv).",
             f"- **Celdas en el borde** (<{pc(ctl['umbral_borde_pp'])} de la fila): {len(borde)}. El modelo no puede dar menos de 0, así que una celda en 0,0 % quiere decir «pocos, sin poder decir cuántos», no «nadie». "
             "En el sankey llevan ‡ en la fila y una nota al pasar el cursor.", ""]
    rows += [f"  - {b['origen']} → {b['destino']}: {pc(b['pct'], 2)} (p95 {pc(b['p95_pct'], 2)})" for b in borde if M.loc[b["origen"]].sum()/M.values.sum() >= .01]
    rows += ["  - Las filas de menos de 1 % del padrón con celdas en el borde están en el CSV.", "",
             f"- Error territorial ponderado con la matriz de cada región: {num(ctl['rmse_territorial_pp'])} puntos.",
             f"- Entre la principal y Calvo se redistribuyen {fmt(ctl['votos_distintos_vs_calvo'])} votos ({pc(100*ctl['votos_distintos_vs_calvo']/ctl['electores'], 2)} de la masa modelada).",
             f"- Destinos por UF con más del 125 % de sus votos reales + 2.000: {len(ctl['alertas_marginales'])}.", "",
             "| Variante | Unidades | Electores | Mayor cambio en una celda |", "|---|---:|---:|---:|"]
    for s in ctl["sensibilidad"]:
        rows.append(f"| {s['escala']} | {fmt(s['unidades'])} | {fmt(s['electores'])} | {num(s['max_diferencia_pp'], 2)} puntos |")
    rows += ["", "Las mayores diferencias recaen en filas pequeñas. La versión estricta cambia la muestra.", "",
             "## Destinos: observados frente a estimados en las secciones usadas", "",
             "| Destino | Observado | Estimado | Diferencia |", "|---|---:|---:|---:|"]
    for c in M.columns:
        obs, pred = ctl["marginal_destino"][c], ctl["marginal_destino_estimada"][c]
        rows.append(f"| {c} | {fmt(obs)} | {fmt(pred)} | {fmt(pred-obs)} |")
    rows += ["", "## Archivos y reproducción", "",
             "[Matriz porcentual](matriz_pct.csv), [votos estimados](matriz_votos.csv), [intervalos y rango de modelos](intervalos.csv), [variante Calvo](calvo_nacional.csv), "
             "[matriz por UF](por_provincia.csv), [matriz por región](por_region.csv), [control completo](control.json), [controles marginales](control_marginales_uf.csv), "
             "[cobertura](cobertura_por_uf.csv), [exclusiones](exclusiones.csv), [fallos de calidad](fallos_calidad.csv), [códigos de candidatos](candidatos_codigos.csv); "
             "matrices de sensibilidad `matriz_votos_{local,munzona,estricta}.csv`.", "", "Desde la raíz:", "", "```",
             "python -X utf8 transferencias/brasil2026_datos.py", "python -X utf8 transferencias/brasil2026_datos.py --preparar",
             "python -X utf8 transferencias/brasil2026_datos.py --cotejar", "python -X utf8 transferencias/brasil2026_estimar.py --preparar",
             "python -X utf8 transferencias/brasil2026_regiones.py", "python -X utf8 transferencias/brasil2026_estimar.py",
             "python -X utf8 transferencias/brasil2026_presentar.py", "python -X utf8 transferencias/brasil2026_revisar_html.py",
             "python -X utf8 transferencias/brasil2026_verificar.py", "python -X utf8 transferencias/auditar.py", "```", "",
             f"WORKERS=4 y BOOT=200 por defecto, con prioridad baja; la corrida completa tardó {fmt(ctl['segundos']/60)} minutos. "
             "Un ZIP local solo se reutiliza si coincide su SHA256 guardado. Para una actualización, no reutilizar `pareadas.pkl` de una versión anterior."]
    (OUT/"RESUMEN.md").write_text("\n".join(rows)+"\n", encoding="utf8")
    print("Sankey e informe generados")


if __name__ == "__main__":
    main()
