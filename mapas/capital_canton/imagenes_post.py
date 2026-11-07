"""Imágenes del segundo tuit (7-nov-2026): 1954 por las 20 secciones del CD y por las 14 circunscripciones,
y 2003 (Jefe de Gobierno, 2.ª vuelta) varones contra mujeres.
    python mapas/capital_canton/imagenes_post.py
Captura el visor en 16:9 (modo claro, sin la barra de controles) y escribe img/post_*.png. Imprime los totales de la
ciudad que muestra el panel, para verificar las cifras del tuit."""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "file:///" + os.path.join(HERE, "capital_1864_2007.html").replace(os.sep, "/")
OUT = os.path.join(HERE, "img")
VISTAS = [("post_1954_secciones", "n=62&m=gan&s=T&g=cd20"), ("post_1954_circunscripciones", "n=62&m=gan&s=T"),
          ("post_2003_varones", "n=101&m=gan&s=V"), ("post_2003_mujeres", "n=101&m=gan&s=M")]


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1440, "height": 810}, device_scale_factor=1.5)
        pg.add_init_script('try{localStorage.setItem("tema","light")}catch(e){}')
        for nombre, h in VISTAS:
            pg.goto("about:blank")
            pg.goto(f"{SRC}#{h}")
            pg.wait_for_timeout(1500)
            # Solo el título, el mapa y los resultados de la ciudad.
            pg.evaluate("""()=>{document.querySelector('.tope').style.display='none';
              const a=document.querySelector('#ordinario aside');let corta=false;
              [...a.children].forEach(el=>{if(el.tagName==='H2'&&el.id!=='metTitulo')corta=true;if(corta)el.style.display='none'});
              document.querySelector('.pie').style.display='none';document.querySelector('#svg').style.maxHeight="590px";window.scrollTo(0,0)}""")
            print(nombre, "|", pg.locator("h1").inner_text(), "|", " / ".join(
                pg.locator("#res .bar").nth(i).inner_text().replace("\n", " ") for i in range(min(3, pg.locator("#res .bar").count()))))
            pg.screenshot(path=os.path.join(OUT, nombre + ".png"))   # 16:9, para la grilla de cuatro fotos de X
        b.close()


if __name__ == "__main__":
    main()
