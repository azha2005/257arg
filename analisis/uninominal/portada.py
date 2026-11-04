"""Portada social (og:image, 1200x630) y miniaturas del índice del sitio para mapa_257.html (4-nov-2026).
    python analisis/uninominal/portada.py
Abre la página con Playwright (Chrome del sistema), toma el mapa del país y el hemiciclo del plan neutral
(límites libres, todos los partidos por separado, diputados 2025) y los compone en una tarjeta con el estilo Ink
de la página. Las cifras salen de la página misma, no se escriben a mano.
Salidas: analisis/uninominal/portada.png (se publica como uninominal/portada.png) y
sitio/miniaturas/uninominal__index{,_claro}.webp (oscura y clara, como las demás tarjetas del índice)."""
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = "file:///" + os.path.join(HERE, "mapa_257.html").replace(os.sep, "/")
MINIS = os.path.join(ROOT, "sitio", "miniaturas")

# La tarjeta se arma sobre la página: se mueven el mapa y el hemiciclo a un marco fijo y se oculta el resto.
COMPONER = r"""
([w, h, oscuro, mini]) => {
  // filas de la tabla de bancas: [fuerza, bancas, % bancas, % votos] y el color de su muestra
  const filas = [...document.querySelectorAll('#res table tbody tr')].map(tr =>
    [...[...tr.cells].map(c => c.textContent.trim()), tr.querySelector('.sw').style.background]);
  const mapa = document.querySelector('#mN'), hemi = document.querySelector('#res .hemi svg');
  const n = s => s.replace(/\s/g, '').replace('.', ',').replace('%', ' %');   // 54.8 % -> 54,8 %
  mapa.querySelectorAll('rect').forEach(r => { if (getComputedStyle(r).strokeDasharray !== 'none') r.remove(); });   // marco del AMBA
  const box = document.createElement('div');
  box.id = 'tarjeta';
  const ink = oscuro ? '#f2f2ef' : 'oklch(16% 0 0)', mut = oscuro ? '#a8a8a3' : 'oklch(44% 0 0)',
        fondo = oscuro ? '#141619' : 'oklch(99.5% 0.003 100)', regla = oscuro ? '#3a3a38' : 'oklch(89% 0.004 100)',
        acento = oscuro ? '#5cc6c0' : 'oklch(50% 0.095 188)';
  box.style.cssText = `position:fixed;inset:0 auto auto 0;width:${w}px;height:${h}px;z-index:99;background:${fondo};
    display:grid;grid-template-columns:auto 1fr;gap:${mini?18:44}px;padding:${mini?22:34}px ${mini?24:56}px;box-sizing:border-box;
    font-family:Epilogue,system-ui,sans-serif;color:${ink};overflow:hidden`;
  const izq = document.createElement('div');
  izq.style.cssText = 'height:100%;display:flex;align-items:center';
  mapa.style.cssText = `height:${h - (mini?44:68)}px;width:auto;display:block`;
  izq.appendChild(mapa);
  const der = document.createElement('div');
  der.style.cssText = `display:flex;flex-direction:column;justify-content:center;min-width:0;gap:${mini?10:13}px`;
  const k = mini ? 0.62 : 1;
  der.innerHTML = `
    <div style="font-size:${17*k}px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:${acento}">${mini ? 'Ejercicio · censo 2022' : 'Atlas electorales argentinos · ejercicio'}</div>
    <div style="font-size:${mini?38:58}px;font-weight:700;letter-spacing:-.04em;line-height:.98">${mini ? '257 distritos<br>uninominales' : 'Argentina con 257<br>distritos uninominales'}</div>
    ${mini ? '' : `<div style="font-size:21px;line-height:1.35;color:${mut};max-width:40ch">Un diputado por distrito, dibujados por algoritmo sobre el censo 2022.</div>`}
    <div id="hemiwrap" style="display:flex;flex-direction:${mini?'column':'row'};align-items:${mini?'flex-start':'flex-end'};gap:${mini?12:26}px;margin-top:${mini?2:10}px;padding-top:${mini?10:18}px;border-top:1px solid ${regla}"></div>
    ${mini ? '' : `<div style="font-size:18px;line-height:1.35;color:${mut}">Diputados 2025, plan neutral; gana la fuerza más votada en cada distrito<br><span style="color:${ink};font-weight:600">azha2005.github.io/257arg/uninominal</span></div>`}`;
  const hw = der.querySelector('#hemiwrap');
  hemi.style.cssText = `width:${mini?250:340}px;height:auto;display:block;flex:none`;
  hw.appendChild(hemi);
  const cif = document.createElement('div');
  cif.style.cssText = mini ? 'display:grid;grid-template-columns:auto auto;gap:3px 16px;font-size:14px;line-height:1.15'
                           : 'display:grid;grid-template-columns:auto auto 1fr auto;align-items:baseline;gap:2px 10px;font-size:18px;line-height:1.1';
  const sw = c => `<span style="width:${mini?10:14}px;height:${mini?10:14}px;border-radius:3px;background:${c};align-self:center"></span>`;
  cif.innerHTML = filas.map((f, i) => mini
    ? `<div style="display:flex;align-items:baseline;gap:6px;white-space:nowrap">${sw(f[4])}<b style="font-size:${i < 2 ? 22 : 15}px;font-variant-numeric:tabular-nums">${f[1]}</b><span>${f[0].replace('La Libertad Avanza', 'LLA')}</span></div>`
    : `${sw(f[4])}<b style="font-size:${i < 2 ? 34 : 22}px;letter-spacing:-.03em;font-variant-numeric:tabular-nums;text-align:right">${f[1]}</b>
       <span style="white-space:nowrap">${f[0]}</span><span style="color:${mut};font-size:16px;text-align:right">${n(f[3])}</span>`).join('');
  hw.appendChild(cif);
  box.append(izq, der);
  document.body.appendChild(box);
  document.documentElement.style.overflow = 'hidden';
  return filas.map(f => f.slice(0, 4));
}
"""


def captura(pg, w, h, oscuro, mini):
    pg.set_viewport_size({"width": w, "height": h})
    pg.emulate_media(color_scheme="dark" if oscuro else "light")   # la miniatura oscura usa el modo oscuro de la página
    pg.goto("about:blank")
    pg.goto(SRC + "#modo=0&dep=0&ren=full&elec=2&pt=1&dl=0")
    pg.wait_for_selector("#res .hemi svg")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(1200)
    info = pg.evaluate(COMPONER, [w, h, oscuro, mini])
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(400)
    return info, Image.open(io.BytesIO(pg.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}))).convert("RGB")


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(device_scale_factor=2)
        info, im = captura(pg, 1200, 630, False, False)
        print("cifras de la página:", info)
        im.resize((1200, 630), Image.LANCZOS).save(os.path.join(HERE, "portada.png"), optimize=True)
        os.makedirs(MINIS, exist_ok=True)
        for oscuro, suf in ((True, ""), (False, "_claro")):
            _, im = captura(pg, 640, 550, oscuro, True)
            im.resize((640, 550), Image.LANCZOS).save(os.path.join(MINIS, f"uninominal__index{suf}.webp"), "WEBP", quality=80, method=6)
        b.close()
    print("portada.png y miniaturas listas")


if __name__ == "__main__":
    main()
