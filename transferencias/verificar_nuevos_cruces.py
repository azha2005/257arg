"""Valida las matrices y el selector de los nuevos cruces; renderiza sus PNG."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright
import estimar
import sankey
from auditar import auditar

HERE = Path(__file__).resolve().parent
PAIRS = [(2013, 2017)] + [(o, d) for o in ("2015p", "2015b") for d in ("2023p", "2023b")]
PAIRS += [(o, d) for o in (2013, 2009) for d in ("2015p", "2015b")]
PAIRS += [(2017, "2019p"), (2017, 2019), ("2015p", "2019p"), ("2015b", "2019p")]
PAIRS += [('1989p','1995p'), ('1989d','1994c'), ('1985d','1987d')]
PAIRS += [('1983p','1989p'), ('1987d','1989p'), ('1985d','1989p')]
PAIRS += [('1989p','1997d')]
PAIRS += [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]
PAIRS += [('1914d','1916d')]


def verify(page, origin, destination):
    folder = HERE / f"{origin}_{destination}"
    sankey.main(origin, destination)
    ctl = json.loads((folder / "control.json").read_text(encoding="utf8"))
    A, B, *_, prepared = estimar.prepare(origin, destination)
    assert prepared["usados"] == ctl["usados"]
    assert prepared["electores_origen_usados"] == ctl["electores_origen_usados"]
    assert prepared["electores_destino_usados"] == ctl["electores_destino_usados"]
    assert ctl['marginal_origen'] == A.sum().astype(int).to_dict()
    assert ctl['marginal_destino'] == B.sum().astype(int).to_dict()
    M = pd.read_csv(folder / "matriz_votos.csv", index_col=0)
    C = pd.read_csv(folder / "calvo_nacional.csv", index_col=0)
    I = pd.read_csv(folder / "intervalos.csv")
    P = pd.read_csv(folder / "por_provincia.csv", dtype={"distrito": str})
    assert np.isfinite(M.values).all() and (M.values >= 0).all()
    assert abs(M.values.sum() - B.values.sum()) <= M.size
    assert abs(C.values.sum() - B.values.sum()) <= C.size
    assert len(I) == M.size and (I.p5 <= I.p95).all()
    assert not P.duplicated(["distrito", "origen", "destino"]).any()
    historical = origin in ('1989p','1989d','1985d','1983p','1987d','1995p','1914d')
    exceptions={('1995p','1999p'):22,('1983p','1985d'):24,('1914d','1916d'):7}
    expected=exceptions.get((origin,destination),23 if historical and (origin,destination) not in [('1989p','1995p'),('1989d','1994c')] else 24)
    assert P.distrito.nunique() == expected
    for district, group in P.groupby("distrito"):
        for name, votes in ctl["marginal_destino_provincia"][district].items():
            if votes == 0:
                assert group.loc[group.destino == name, "votos"].sum() == 0
    uri = (folder / f"sankey_{origin}_{destination}.html").as_uri()
    page.goto(uri)
    options = page.locator("#v option").evaluate_all("xs=>xs.map(x=>({value:x.value,name:x.textContent}))")
    assert len(options) == P.distrito.nunique()+1
    page.screenshot(path=str(folder / f"sankey_{origin}_{destination}.png"), full_page=True)
    for option in options:
        key = option["value"]
        page.select_option("#v", key)
        assert page.locator(".vista:visible").count() == 1
        assert page.locator(".vista:visible").get_attribute("id") == "v-" + key
        assert page.evaluate("location.hash") == "#" + key
        if key == "nacional":
            continue
        text = page.locator(".vista:visible svg > text").all_text_contents()
        assert option["name"] in text[0]
        group = P[P.distrito == key]
        total = group.votos.sum()
        for category, votes in group.groupby("destino").votos.sum().items():
            if votes > 0:
                expected = category + ": " + ("%.1f" % (100 * votes / total)).replace(".", ",") + " %"
                assert expected in text, (origin, destination, key, expected)
        if (origin, destination) == (2013, 2017) and key in ("01", "21", "24"):
            page.screenshot(path=str(folder / ("selector_" + key + ".png")), full_page=True)
        if (origin,destination)==('1983p','1985d') and key=='02':
            page.screenshot(path=str(folder/'PBA_1983p_1985d.png'),full_page=True)
        if origin=='1914d' and key in ('01','02'):
            page.screenshot(path=str(folder/('Capital_1914_1916.png' if key=='01' else 'PBA_1914_1916.png')),full_page=True)
    page.goto(uri + "#04")
    page.wait_for_function("document.getElementById('v').value === '04'")
    page.reload()
    assert page.locator("#v").input_value() == "04"
    audit = auditar(f"{origin}_{destination}")
    used = A.sum(axis=1).rename("electores_origen").to_frame().join(B.sum(axis=1).rename("electores_destino"))
    used.to_csv(folder / "unidades_utilizadas.csv", encoding="utf-8-sig")
    summary = dict(par=f"{origin}_{destination}", controles="OK", vistas=len(options),
                   usados=ctl["usados"], cobertura_origen=100 * ctl["electores_origen_usados"] / ctl["electores_origen_total"],
                   por_seccion=ctl["por_seccion"], unidades=ctl["unidades_por_provincia"],
                   no_identificadas=[f["origen"] for f in audit["filas"] if f["no_identificada"]],
                   cerca_promedio=[f["origen"] for f in audit["filas"] if f["cerca_promedio"]],
                   alertas_provinciales=audit["imposibles"], separacion=audit["separacion"])
    counts = {k: sum(p[k] for p in ctl["unidades_por_provincia"].values())
              for k in ("circuitos", "grupos_circuitos", "departamentos")}
    fmt = lambda x: f"{x:.2f}".replace(".", ",")
    report = [f"# Transferencias {origin} → {destination}", "",
              "Estimaciones ecológicas, no observaciones de cambios individuales de voto.", "",
              f"[Abrir gráfico con selector provincial](sankey_{origin}_{destination}.html) | [PNG](sankey_{origin}_{destination}.png)", "",
              f"Base usada: {counts['circuitos']} circuitos, {counts['grupos_circuitos']} grupos y {counts['departamentos']} departamentos.",
              f"Cobertura del padrón de origen: **{fmt(summary['cobertura_origen'])} %** ({ctl['electores_origen_usados']:,} de {ctl['electores_origen_total']:,}).",
              f"Penalización elegida por validación cruzada: {ctl['lambda']}; separación: {audit['separacion']} puntos.", "",
              "Filas no identificadas: " + (", ".join(summary["no_identificadas"]) or "ninguna según el umbral de la auditoría") + ".",
              "Filas cerca del promedio: " + (", ".join(summary["cerca_promedio"]) or "ninguna") + ".",
              f"Sensibilidad principal / Calvo: cambian {ctl['votos_distintos_vs_calvo']:,} votos ({fmt(100*ctl['votos_distintos_vs_calvo']/ctl['votos_total'])} % del total modelado).",
              "El bootstrap no mide toda esta sensibilidad a la especificación.", "",
              "[Correspondencias y fuentes documentales](../correspondencias_2013_2017/LEEME.md). " + ctl["correspondencias"]["reserva"], "",
              "[Matriz porcentual](matriz_pct.csv), [votos estimados](matriz_votos.csv), [intervalos](intervalos.csv), "
              "[variante Calvo](calvo_nacional.csv), [matriz provincial](por_provincia.csv), [unidades usadas](unidades_utilizadas.csv), "
              "[transformaciones](correspondencias.csv), [control completo](control.json).", "",
              "Alertas provinciales de la auditoría: " + (json.dumps(audit["imposibles"], ensure_ascii=False) if audit["imposibles"] else "ninguna") + ".", ""]
    (folder / "RESUMEN.md").write_text("\n".join(report), encoding="utf8")
    if historical:
        report_text = '\n'.join(report).replace('Cobertura del padrón de origen','Cobertura de los votos desglosados de origen')
        report_text = report_text.replace('../correspondencias_2013_2017/LEEME.md','../historicos_1989/LEEME.md')
        report_text += '\nNo incluye abstención. Las unidades incluyen circunscripciones de Capital y uniones territoriales completas. Las exclusiones por calidad están en control.json.\n'
        if origin == '1987d' or (origin,destination)==('1985d','1987d'): report_text += '\nTierra del Fuego no eligió diputados en 1987; el selector contiene 23 distritos.\n'
        if (origin,destination) in [('1983p','1989p'),('1985d','1989p')]: report_text += '\nTierra del Fuego queda fuera por superar el filtro común de crecimiento del volumen de votos; no se estima una matriz provincial con esas unidades descartadas. Hay 23 distritos.\n'
        if destination == '1997d': report_text += '\nSan Luis no tiene datos departamentales de diputados 1997 en la base: queda fuera del ajuste y del selector; no se distribuye el total provincial. Hay 23 distritos.\n'
        if destination == '1999p': report_text += '\nLa base presidencial 1999 no incluye San Luis ni Santa Cruz. Quedan fuera del ajuste y del selector: 22 distritos. La extrapolación de Deseado 1995 se conserva en la fuente de origen pero esa unidad no interviene en este cruce. No se usó la imputación de fuerzas menores de otras bases del proyecto.\n'
        if (origin,destination)==('1983p','1985d'): report_text += '\n[Buenos Aires: 125 partidos, comparación entre modelos e intervalos provinciales](PBA.md) | [Abrir PBA](sankey_1983p_1985d.html#02).\n'
        diagnostic = folder/'diagnostico.json'
        if diagnostic.exists():
            dg = json.loads(diagnostic.read_text(encoding='utf8'))
            report_text += f"\nDiagnóstico interno: mejora del error frente al promedio provincial {dg['mejora_modelo_pct']:.1f} %. [Detalles y utilidad](../historicos_1989/LEEME.md), [diagnóstico](diagnostico.json).\n"
        (folder / 'RESUMEN.md').write_text(report_text,encoding='utf8')
        if origin=='1914d':
            report_text=report_text.replace('../historicos_1989/LEEME.md','../fuentes_1914_1916/LEEME.md')
            report_text=report_text.replace('Cobertura de los votos desglosados de origen','Cobertura del voto en la selección legible de 1914 (no del país)')
            report_text+='\nCobertura parcial de siete jurisdicciones. Solo votos partidarios/primer candidato publicado, sin blancos, nulos ni abstención. No se usaron estimaciones del atlas ni totales provinciales repetidos.\n\n[Buenos Aires](PBA.md) | [Capital Federal](Capital.md) | [Sensibilidad a fuentes y filtro](sensibilidad.json) | [Revisión Cacopardo de los demás cruces](../revision_cacopardo_1967/LEEME.md).\n'
            (folder/'RESUMEN.md').write_text(report_text,encoding='utf8')
    print(summary["par"], "OK", flush=True)
    return summary


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        selected = PAIRS[-1:] if '--1914' in sys.argv else PAIRS[20:23] if '--tanda95' in sys.argv else PAIRS[13:] if '--solo-historicos' in sys.argv else PAIRS[9:13] if "--solo-2019" in sys.argv else PAIRS
        result = [verify(page, *pair) for pair in selected]
        assert not errors, errors
        browser.close()
    if "--solo-2019" in sys.argv or '--solo-historicos' in sys.argv or '--tanda95' in sys.argv or '--1914' in sys.argv:
        previous = json.loads((HERE / "VERIFICACION_NUEVOS_CRUCES.json").read_text(encoding="utf8"))
        fresh = {item["par"] for item in result}
        result = [item for item in previous if item["par"] not in fresh] + result
    (HERE / "VERIFICACION_NUEVOS_CRUCES.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    lines = ["# Cruces solicitados: índice y verificación", "",
             "Cada HTML incluye una vista conjunta y selector provincial. 1914d→1916d tiene cobertura parcial de siete jurisdicciones. Los cruces con 1987d tienen 23 distritos porque Tierra del Fuego no votó; 1983p/1985d→1989p excluyen ese distrito por el filtro de crecimiento; 1997d tiene 23 porque falta San Luis; 1999p tiene 22 porque faltan San Luis y Santa Cruz. Los demás tienen 24. Las cintas muestran votos y porcentajes al pasar el cursor.", "",
             "| Par | Gráfico | Resumen y reservas | Unidades | Cobertura origen |",
             "|---|---|---|---:|---:|"]
    for item in result:
        par = item["par"]
        lines.append(f"| {par} | [HTML]({par}/sankey_{par}.html) | [Resumen]({par}/RESUMEN.md) | {item['usados']} | {item['cobertura_origen']:.2f} % |")
    lines += ["", "Verificación: matrices no negativas, conservación de totales al redondeo, intervalos ordenados, "
              f"destinos ausentes en cero, correspondencias conservando categorías, {sum(item['vistas'] for item in result)} vistas con porcentajes cotejados contra CSV, "
              "enlaces directos por provincia y ausencia de errores JavaScript.", "",
              "[Fuentes y pendientes de correspondencias](correspondencias_2013_2017/LEEME.md). "
              "`p`: general presidencial; `b`: balotaje; `d`: diputados; `1994c`: constituyentes. 2009, 2013 y 2017 sin sufijo: diputados nacionales.", "",
              "Los cruces históricos usan votos desglosados y no incluyen abstención: [fuentes, extrapolación y utilidad](historicos_1989/LEEME.md). Su cobertura no es cobertura del padrón.", ""]
    lines += ['[PBA 1983p→1985d: comparación provincial de modelos](1983p_1985d/PBA.md).','']
    lines += ['[1914–1916: fuentes y cobertura](fuentes_1914_1916/LEEME.md) | [Cacopardo: revisión de los cruces existentes](revision_cacopardo_1967/LEEME.md).','']
    (HERE / "INDICE_NUEVOS_CRUCES.md").write_text("\n".join(lines), encoding="utf8")
