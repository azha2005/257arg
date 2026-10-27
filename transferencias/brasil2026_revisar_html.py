"""Render local con Edge: comprueba las 29 vistas del Sankey (nacional, 27 UF y exterior) y guarda los PNG."""
import json

from playwright.sync_api import sync_playwright

from brasil2026_datos import OUT, dump


def main():
    errors, report = [], {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 900}, device_scale_factor=1.5)
        page.on("pageerror", lambda error: errors.append(str(error)))
        for suf in ["", "_votantes", "_reducido", "_reducido_breve"]:
            name = f"sankey_brasil_2026p_2026b{suf}"
            page.goto((OUT/f"{name}.html").as_uri())
            choices = page.locator("#v option").evaluate_all("xs => xs.map(x => ({value:x.value, name:x.textContent}))")
            assert len(choices) == 29, len(choices)
            page.locator("svg").first.screenshot(path=str(OUT/f"{name}.png"))
            for choice in choices:
                page.select_option("#v", choice["value"])
                assert page.locator(".vista:visible").count() == 1
                visible = page.locator(".vista:visible svg")
                assert visible.locator("path title").count() > 0
                if choice["value"] != "nacional":
                    assert choice["name"] in visible.text_content()
            report[name] = len(choices)
        assert not errors, errors
        browser.close()
    report = dict(estado="OK", vistas=report, errores_js=errors, capturas=["sankey_brasil_2026p_2026b.png", "sankey_brasil_2026p_2026b_votantes.png", "sankey_brasil_2026p_2026b_reducido.png", "sankey_brasil_2026p_2026b_reducido_breve.png"])
    dump(OUT/"VERIFICACION_HTML.json", report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
