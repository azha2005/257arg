// Registro automatico de ventanas de zoom contra el PNG de referencia.
// Se inyecta en una copia del atlas por runreg1.sh (define window.__REF y window.__WANT).
// Busca (escala, origen) de cada inset minimizando la distancia de chamfer entre las lineas blancas de la referencia y las propias.
// Cuidado: las geometrias de los insets de 1999 no son siempre las del mapa base, asi que un costo > ~3 px no es un buen ajuste:
// en ese caso conviene elegir la ventana a ojo (ver references/insets.md).
// Registro de ventanas de zoom contra 1999.png (se inyecta en una copia del atlas)
(async () => {
  document.getElementById('mainwrap').style.cssText+=';--v-rcb:inline;--v-rcc:inline;--v-d:inline';
  const MAIN = window.__MAIN || { s: 0.5425, tx: 544.2, ty: 228.1 };
  const img = new Image(); img.src = window.__REF;   // URL file:/// del PNG de referencia
  await img.decode();
  const rc = document.createElement('canvas'); rc.width = img.width; rc.height = img.height;
  const rx = rc.getContext('2d', { willReadFrequently: true }); rx.drawImage(img, 0, 0);
  const R = rx.getImageData(0, 0, rc.width, rc.height).data;

  const cls = c => [...document.querySelectorAll('#B path.' + c)].map(p => {
    const m = p.getCTM(); const s = MAIN.s;
    const M = [m.a / s, m.b / s, m.c / s, m.d / s, (m.e - MAIN.tx) / s, (m.f - MAIN.ty) / s];
    const b = p.getBBox(); const xs = [], ys = [];
    for (const [x, y] of [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]]) { xs.push(M[0] * x + M[2] * y + M[4]); ys.push(M[1] * x + M[3] * y + M[5]); }
    return { p2: new Path2D(p.getAttribute('d')), M, bb: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)], sc: Math.sqrt(Math.abs(M[0] * M[3] - M[1] * M[2])) };
  });
  const SETS = { d: cls('d'), rcb: cls('rcb'), rcc: cls('rcc') };

  function dt(mask, w, h) { // chamfer 3-4
    const D = new Float32Array(w * h); const INF = 1e6;
    for (let i = 0; i < w * h; i++) D[i] = mask[i] ? 0 : INF;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const i = y * w + x; let v = D[i];
      if (x > 0) v = Math.min(v, D[i - 1] + 1); if (y > 0) v = Math.min(v, D[i - w] + 1);
      if (x > 0 && y > 0) v = Math.min(v, D[i - w - 1] + 1.4); if (x < w - 1 && y > 0) v = Math.min(v, D[i - w + 1] + 1.4); D[i] = v; }
    for (let y = h - 1; y >= 0; y--) for (let x = w - 1; x >= 0; x--) { const i = y * w + x; let v = D[i];
      if (x < w - 1) v = Math.min(v, D[i + 1] + 1); if (y < h - 1) v = Math.min(v, D[i + w] + 1);
      if (x < w - 1 && y < h - 1) v = Math.min(v, D[i + w + 1] + 1.4); if (x > 0 && y < h - 1) v = Math.min(v, D[i + w - 1] + 1.4); D[i] = v; }
    return D;
  }

  function search(name, F, sets, kr, cr, lw) {
    const [fx, fy, fw, fh] = F;
    // máscara de referencia (reducida a escala q)
    function refMask(q) {
      const w = Math.round(fw * q), h = Math.round(fh * q), m = new Uint8Array(w * h);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        // tomar bloque q^-1
        const x0 = Math.floor(fx + x / q), y0 = Math.floor(fy + y / q), x1 = Math.max(x0 + 1, Math.floor(fx + (x + 1) / q)), y1 = Math.max(y0 + 1, Math.floor(fy + (y + 1) / q));
        let hit = 0; for (let yy = y0; yy < y1 && !hit; yy++) for (let xx = x0; xx < x1; xx++) { const i = (yy * rc.width + xx) * 4; if (R[i + 3] > 200 && R[i] > 225 && R[i + 1] > 225 && R[i + 2] > 225) { hit = 1; break; } }
        m[y * w + x] = hit; }
      return { m, w, h };
    }
    const cv = document.createElement('canvas'); const cx = cv.getContext('2d', { willReadFrequently: true });
    const refs = {}; const rdt = {};
    function evalCand(k, vx, vy, q) {
      if (!refs[q]) { refs[q] = refMask(q); rdt[q] = dt(refs[q].m, refs[q].w, refs[q].h); }
      const { m: rm, w, h } = refs[q]; cv.width = w; cv.height = h;
      cx.fillStyle = '#000'; cx.fillRect(0, 0, w, h); cx.strokeStyle = '#fff';
      const kk = k * q; const x1 = vx + w / kk, y1 = vy + h / kk;
      for (const set of sets) for (const e of SETS[set]) {
        if (e.bb[2] < vx || e.bb[0] > x1 || e.bb[3] < vy || e.bb[1] > y1) continue;
        cx.setTransform(kk * e.M[0], kk * e.M[1], kk * e.M[2], kk * e.M[3], kk * (e.M[4] - vx), kk * (e.M[5] - vy));
        cx.lineWidth = Math.max(1, lw * q) / (kk * e.sc); cx.stroke(e.p2); }
      cx.setTransform(1, 0, 0, 1, 0, 0);
      const D = cx.getImageData(0, 0, w, h).data; const mm = new Uint8Array(w * h); let nm = 0, nr = 0;
      for (let i = 0; i < w * h; i++) { if (D[i * 4] > 128) { mm[i] = 1; nm++; } if (rm[i]) nr++; }
      if (nm < 8 || nr < 8) return 1e9;
      const mdt = dt(mm, w, h); let a = 0, b = 0; const cap = 6 * q;
      for (let i = 0; i < w * h; i++) { if (mm[i]) a += Math.min(rdt[q][i], cap); if (rm[i]) b += Math.min(mdt[i], cap); }
      return (a / nm + b / nr) / q;
    }
    let cands = [];
    const [k0, k1] = kr, [cx0, cx1, cy0, cy1] = cr; // rango del CENTRO de la ventana
    const Q=0.2;
    for (let k = k0; k <= k1; k *= 1.12) {
      const step = 7 / k;
      for (let cxx = cx0; cxx <= cx1; cxx += step) for (let cyy = cy0; cyy <= cy1; cyy += step) {
        const vx = cxx - fw / k / 2, vy = cyy - fh / k / 2;
        const c = evalCand(k, vx, vy, Q); if (c < 1e8) cands.push([c, k, vx, vy]); }
    }
    cands.sort((a, b) => a[0] - b[0]); cands = cands.slice(0, 10);
    // refinar
    let best = null;
    for (const [, k, vx, vy] of cands) {
      let bk = k, bx = vx, by = vy, bc = evalCand(k, vx, vy, 1);
      for (const [dk, dpx] of [[0.03, 4], [0.012, 2], [0.005, 1], [0.002, 0.5]]) {
        for (let it = 0; it < 4; it++) {
          let imp = false;
          for (const sk of [-1, 0, 1]) for (const sx of [-1, 0, 1]) for (const sy of [-1, 0, 1]) {
            if (!sk && !sx && !sy) continue; const k2 = bk * (1 + sk * dk), x2 = bx + sx * dpx / bk, y2 = by + sy * dpx / bk;
            const c = evalCand(k2, x2, y2, 1); if (c < bc) { bc = c; bk = k2; bx = x2; by = y2; imp = true; } }
          if (!imp) break; } }
      if (!best || bc < best[0]) best = [bc, bk, bx, by]; }
    return { name, cost: +best[0].toFixed(3), k: +best[1].toFixed(4), vx: +best[2].toFixed(2), vy: +best[3].toFixed(2), win: [+best[2].toFixed(2), +best[3].toFixed(2), +(fw / best[1]).toFixed(2), +(fh / best[1]).toFixed(2)] };
  }

  const out = [];
  const want = (window.__WANT || 'tuc,sj,mza,res,amba,caba').split(',');
  const job = {
    tuc: () => search('tuc', [452, 303, 196, 178], ['d'], [3, 14], [600, 690, 230, 340], 2),
    sj: () => search('sj', [331, 548, 315, 153], ['d'], [3, 22], [380, 450, 600, 680], 2),
    mza: () => search('mza', [331, 786, 218, 181], ['d'], [3, 22], [385, 465, 725, 785], 2),
    res: () => search('res', [1416, 502, 458, 203], ['d'], [3, 16], [1040, 1130, 300, 370], 2),
    amba: () => search('amba', [1250, 788, 641, 314], ['rcb', 'rcc'], [0.7, 3], [1100, 1350, 1600, 1850], 2),
    caba: () => search('caba', [1630, 1185, 195, 235], ['rcc'], [1, 12], [1240, 1300, 1710, 1770], 2)
  };
  for (const n of want) { const t0 = performance.now(); try { out.push(Object.assign(job[n](), { ms: Math.round(performance.now() - t0) })); } catch (e) { out.push({ name: n, err: String(e) }); } await new Promise(r => setTimeout(r, 0)); }
  const pre = document.createElement('pre'); pre.id = 'res'; pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
})();
