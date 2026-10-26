
() => {
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.querySelector("#atlas");
  svg.querySelectorAll(".tile").forEach(t => t.remove());
  svg.querySelectorAll(".sel,.dim").forEach(e => e.classList.remove("sel", "dim"));
  // 1) cada <use href="#B"> pasa a ser una copia real de #B (las variables CSS del <use> se heredan igual)
  svg.querySelectorAll("use").forEach(u => {
    const ref = document.querySelector(u.getAttribute("href"));
    const cl = ref.cloneNode(true);   // conserva el id: los selectores '#B ...' del CSS siguen valiendo
    cl.setAttribute("style", (ref.getAttribute("style") || "") + ";" + (u.getAttribute("style") || ""));
    const w = document.createElementNS(NS, "g");
    const x = +u.getAttribute("x") || 0, y = +u.getAttribute("y") || 0;
    const tr = ((u.getAttribute("transform") || "") + (x || y ? ` translate(${x} ${y})` : "")).trim();
    if (tr) w.setAttribute("transform", tr);
    w.appendChild(cl); u.replaceWith(w);
  });
  // 2) estilos calculados a atributos; se quita lo que no se dibuja
  const SHAPE = new Set(["path", "rect", "circle", "ellipse", "line", "polygon", "polyline", "text"]);
  const SKIP = new Set(["defs", "clipPath", "style", "filter", "title", "desc", "linearGradient", "radialGradient", "pattern"]);
  const texts = [];
  const px = v => parseFloat(v);
  (function walk(el) {
    for (const c of [...el.children]) {
      const tag = c.localName;
      if (SKIP.has(tag)) continue;
      const cs = getComputedStyle(c);
      if (cs.display === "none" || cs.visibility === "hidden") { c.remove(); continue; }
      if (SHAPE.has(tag)) {
        const set = (k, v) => c.setAttribute(k, v);
        if (c.dataset.i !== undefined) try {   // nombre y resultado de la unidad, para el <title> (como el mapa de 2019 de es.wikipedia)
          const i = +c.dataset.i, T = DATA.territories[i], u = DATA.modes[MI].units[i];
          let s = T.n + " (" + T.p + ")";
          if (u && u.lines) s += u.lines.map(l => "\n" + (DATA.candidates[l[0]] ? DATA.candidates[l[0]].n : l[0]) + ": " + l[1] + " (" + String(l[2]).replace(".", ",") + " %)").join("");
          if (u && u.metrics) s += u.metrics.filter(m => m[0] !== "Inscriptos" && m[0] !== "Votantes").map(m => "\n" + m[0] + ": " + m[1]).join("");
          set("data-title", s);
        } catch (e) { /* sin titulo si el dataset no trae esos campos */ }
        set("fill", cs.fill); set("stroke", cs.stroke);
        if (cs.stroke !== "none") {
          set("stroke-width", px(cs.strokeWidth)); set("stroke-linejoin", cs.strokeLinejoin); set("stroke-linecap", cs.strokeLinecap);
          if (cs.strokeOpacity !== "1") set("stroke-opacity", cs.strokeOpacity);
          if (cs.paintOrder !== "normal") set("paint-order", cs.paintOrder);
        } else { c.removeAttribute("stroke-width"); }
        if (cs.fillOpacity !== "1") set("fill-opacity", cs.fillOpacity);
        if (cs.opacity !== "1") set("opacity", cs.opacity);
        if (cs.fillRule !== "nonzero") set("fill-rule", cs.fillRule);
        if (tag === "text") {
          const bb = c.getBBox();
          texts.push({ w: bb.width, tl: c.getAttribute("textLength"), fs: px(cs.fontSize), fw: +cs.fontWeight, it: cs.fontStyle === "italic",
                       anchor: cs.textAnchor, ls: cs.letterSpacing === "normal" ? 0 : px(cs.letterSpacing) });
          c.setAttribute("data-t", texts.length - 1);
        }
      } else {
        if (cs.opacity !== "1") c.setAttribute("opacity", cs.opacity);
        walk(c);
      }
      if (tag !== "text") for (const a of ["class", "style"]) c.removeAttribute(a);
      else { c.removeAttribute("class"); c.removeAttribute("style"); }
    }
  })(svg);
  // 3) cada recuadro conserva solo las formas que caen dentro de su ventana (con margen por el slice/meet)
  let podadas = 0;
  svg.querySelectorAll("svg[viewBox]").forEach(s => {
    if (s === svg) return;
    const [vx, vy, vw, vh] = s.getAttribute("viewBox").split(/[ ,]+/).map(Number), mg = Math.max(vw, vh) * 0.6;
    s.querySelectorAll("path,rect,circle").forEach(e => {
      const b = e.getBBox();
      if (b.x > vx + vw + mg || b.x + b.width < vx - mg || b.y > vy + vh + mg || b.y + b.height < vy - mg) { e.remove(); podadas++; }
    });
  });
  svg.querySelectorAll("style").forEach(s => s.remove());
  svg.removeAttribute("id");
  return { texts, xml: new XMLSerializer().serializeToString(svg) };
}
