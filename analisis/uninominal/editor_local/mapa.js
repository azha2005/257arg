"use strict";

const formatInt = new Intl.NumberFormat("es-AR", {maximumFractionDigits: 0});
const formatDecimal = new Intl.NumberFormat("es-AR", {minimumFractionDigits: 1, maximumFractionDigits: 1});

function unionBounds(a, b) {
  return [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])];
}

const emptyBounds = () => [Infinity, Infinity, -Infinity, -Infinity];

class MapaDistritos {
  constructor(canvas, events) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", {alpha: false});
    this.events = events;
    this.camera = {x: 0, y: 0, z: 0.01};
    this.plan = null;
    this.gesture = null;
    this.frame = 0;
    this.hoverIndex = -1;
    this.resize = new ResizeObserver(() => this.resizeToCanvas());
    this.resize.observe(canvas);
    canvas.addEventListener("pointerdown", event => this.pointerDown(event));
    canvas.addEventListener("pointermove", event => this.pointerMove(event));
    canvas.addEventListener("pointerup", event => this.pointerEnd(event));
    canvas.addEventListener("pointercancel", event => this.pointerEnd(event));
    canvas.addEventListener("lostpointercapture", event => this.pointerEnd(event));
    canvas.addEventListener("pointerleave", () => {
      if (!this.gesture) this.hover(-1);
    });
    canvas.addEventListener("wheel", event => {
      if (!this.plan) return;
      event.preventDefault();
      const delta = event.deltaY * (event.deltaMode === 1 ? 18 : event.deltaMode === 2 ? 130 : 1);
      this.zoom(Math.exp(Math.max(-3, Math.min(3, -delta / 520))), ...this.point(event));
    }, {passive: false});
  }

  show(plan) {
    this.plan = plan;
    this.grid = new Map();
    this.paths = new Array(plan.units.length);
    this.step = Math.max(plan.base.ancho, plan.base.alto) / 64;
    this.bounds = plan.units.map((unit, index) => {
      const b = emptyBounds();
      for (const ring of unit[5]) {
        for (let i = 0; i < ring.length; i += 2) {
          b[0] = Math.min(b[0], ring[i]);
          b[1] = Math.min(b[1], ring[i + 1]);
          b[2] = Math.max(b[2], ring[i]);
          b[3] = Math.max(b[3], ring[i + 1]);
        }
      }
      this.eachCell(b, key => {
        if (!this.grid.has(key)) this.grid.set(key, []);
        this.grid.get(key).push(index);
      });
      return b;
    });
    this.hover(-1);
    this.fit();
  }

  eachCell(bounds, visit) {
    const cell = value => Math.max(0, Math.min(65, Math.floor(value / this.step)));
    for (let y = cell(bounds[1]); y <= cell(bounds[3]); y++) {
      for (let x = cell(bounds[0]); x <= cell(bounds[2]); x++) visit(66 * y + x);
    }
  }

  candidates(bounds) {
    const chosen = new Set();
    this.eachCell(bounds, cell => {
      for (const index of this.grid.get(cell) ?? []) {
        const [left, top, right, bottom] = this.bounds[index];
        if (!(left > bounds[2] || right < bounds[0] || top > bounds[3] || bottom < bounds[1])) {
          chosen.add(index);
        }
      }
    });
    return chosen;
  }

  resizeToCanvas() {
    const {clientWidth: width, clientHeight: height} = this.canvas;
    if (!width || !height) return;
    const formerWidth = this.width;
    const formerHeight = this.height;
    if (this.width) {
      this.camera.x += (width - this.width) / 2;
      this.camera.y += (height - this.height) / 2;
    }
    this.width = width;
    this.height = height;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = Math.round(width * this.dpr);
    this.canvas.height = Math.round(height * this.dpr);
    if (this.plan && this.fittedDistrict !== undefined && (width !== formerWidth || height !== formerHeight)) {
      this.fit(this.fittedDistrict);
      return;
    }
    this.request();
  }

  fit(district = null) {
    if (!this.plan) return;
    const {ancho, alto} = this.plan.base;
    let box = [0, 0, ancho, alto];
    if (district !== null) {
      let combined = emptyBounds();
      this.plan.districts.forEach((d, ix) => {
        if (d === district) combined = unionBounds(combined, this.bounds[ix]);
      });
      if (!Number.isFinite(combined[0])) return;
      box = combined;
    }
    const width = this.width || this.canvas.clientWidth;
    const height = this.height || this.canvas.clientHeight;
    const padding = Math.min(74, width * .18, height * .18);
    this.baseScale = Math.min((width - padding) / ancho, (height - padding) / alto);
    const z = Math.min((width - padding) / Math.max(1, box[2] - box[0]),
                       (height - padding) / Math.max(1, box[3] - box[1]), this.baseScale * 420);
    this.fittedDistrict = district;
    this.camera = {x: width / 2 - (box[0] + box[2]) * z / 2,
                   y: height / 2 - (box[1] + box[3]) * z / 2, z};
    this.request();
  }

  zoom(factor, x = this.width / 2, y = this.height / 2) {
    if (!this.plan) return;
    const [worldX, worldY] = this.world(x, y);
    const z = Math.max(this.baseScale * .28, Math.min(this.baseScale * 420, this.camera.z * factor));
    this.camera = {x: x - worldX * z, y: y - worldY * z, z};
    this.fittedDistrict = undefined;
    this.request();
  }

  world(x, y) {
    const c = this.camera;
    return [(x - c.x) / c.z, (y - c.y) / c.z];
  }

  path(index) {
    if (this.paths[index]) return this.paths[index];
    const p = new Path2D();
    for (const ring of this.plan.units[index][5]) {
      p.moveTo(ring[0], ring[1]);
      for (let i = 2; i < ring.length; i += 2) p.lineTo(ring[i], ring[i + 1]);
      p.closePath();
    }
    this.paths[index] = p;
    return p;
  }

  request() {
    if (!this.frame) this.frame = requestAnimationFrame(() => {
      this.frame = 0;
      this.draw();
    });
  }

  draw() {
    const ctx = this.ctx;
    const {width, height, dpr} = this;
    if (!width || !height) return;
    const color = this.events.style();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = color.water;
    ctx.fillRect(0, 0, width, height);
    if (this.plan) {
      const c = this.camera;
      const grid = Math.max(32, Math.min(100, width / 10));
      ctx.strokeStyle = color.grid;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = (c.x % grid + grid) % grid; x < width; x += grid) {
        ctx.moveTo(x, 0); ctx.lineTo(x, height);
      }
      for (let y = (c.y % grid + grid) % grid; y < height; y += grid) {
        ctx.moveTo(0, y); ctx.lineTo(width, y);
      }
      ctx.stroke();
      ctx.setTransform(c.z * dpr, 0, 0, c.z * dpr, c.x * dpr, c.y * dpr);
      const extents = [...this.world(-2, -2), ...this.world(width + 2, height + 2)];
      const visible = this.candidates(extents);
      const grouped = new Map();
      const detailed = this.bounds.length < 7000 || c.z / this.baseScale > 3;
      for (const index of visible) {
        const district = this.plan.districts[index];
        const fill = color.fill ? color.fill(index, district) : color.district(district);
        const emphasis = district === color.active;
        const key = color.fill ? `${emphasis}:${fill}` : district;
        if (!grouped.has(key)) grouped.set(key, {fill, emphasis, path: new Path2D()});
        grouped.get(key).path.addPath(this.path(index));
      }
      ctx.lineWidth = (detailed ? .65 : .45) / c.z;
      ctx.lineJoin = "round";
      ctx.strokeStyle = color.boundary;
      const layers = [...grouped.values()].sort((a, b) => Number(a.emphasis) - Number(b.emphasis));
      for (const {fill, path} of layers) {
        ctx.fillStyle = fill;
        ctx.fill(path, "evenodd");
        ctx.stroke(path);
      }
      for (const {emphasis, path} of layers) {
        if (!emphasis) continue;
        ctx.strokeStyle = color.hover;
        ctx.globalAlpha = .6;
        ctx.lineWidth = .95 / c.z;
        ctx.stroke(path);
        ctx.globalAlpha = 1;
      }
      if (this.hoverIndex >= 0) {
        const hover = this.path(this.hoverIndex);
        ctx.fillStyle = color.hoverFill;
        ctx.fill(hover, "evenodd");
        ctx.strokeStyle = color.hover;
        ctx.lineWidth = 2 / c.z;
        ctx.stroke(hover);
      }
      this.events.scale(c.z / this.plan.base.escala);
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }

  point(event) {
    const rect = this.canvas.getBoundingClientRect();
    return [event.clientX - rect.left, event.clientY - rect.top];
  }

  hit(screenX, screenY) {
    const [x, y] = this.world(screenX, screenY);
    let candidate = -1;
    for (const index of this.candidates([x, y, x, y])) {
      if (index > candidate && this.ctx.isPointInPath(this.path(index), x, y, "evenodd")) candidate = index;
    }
    return candidate;
  }

  hover(index) {
    if (index === this.hoverIndex) return;
    this.hoverIndex = index;
    this.events.hover(index);
    this.request();
  }

  pointerDown(event) {
    if (!this.plan || !this.events.enabled() || this.gesture ||
        (event.button !== 0 && event.button !== 1)) return;
    const p = this.point(event);
    const tool = event.button === 1 ? "pan" : this.events.tool();
    this.gesture = {id: event.pointerId, tool, p, origin: p, seen: new Set()};
    this.canvas.focus({preventScroll: true});
    this.canvas.setPointerCapture(event.pointerId);
    if (tool !== "pan") {
      this.events.begin();
      this.paint(...p);
    }
    this.canvas.classList.add("dragging");
    event.preventDefault();
  }

  pointerMove(event) {
    if (!this.plan) return;
    const p = this.point(event);
    const g = this.gesture;
    if (!g) {
      this.hover(this.hit(...p));
      return;
    }
    if (g.id !== event.pointerId) return;
    if (g.tool === "pan") {
      this.fittedDistrict = undefined;
      this.camera.x += p[0] - g.p[0];
      this.camera.y += p[1] - g.p[1];
      this.hover(-1);
      this.request();
    } else {
      const radius = this.events.brush();
      const n = Math.min(72, Math.max(1, Math.ceil(Math.hypot(p[0] - g.p[0], p[1] - g.p[1]) / (radius || 3))));
      for (let i = 1; i <= n; i++) {
        this.paint(g.p[0] + (p[0] - g.p[0]) * i / n, g.p[1] + (p[1] - g.p[1]) * i / n);
      }
    }
    g.p = p;
  }

  paint(x, y) {
    const g = this.gesture;
    const indices = [];
    const add = index => {
      if (index >= 0 && !g.seen.has(index)) {
        indices.push(index);
        g.seen.add(index);
      }
    };
    add(this.hit(x, y));
    const r = this.events.brush();
    if (r > 0) {
      const radius = r / this.camera.z;
      const [wx, wy] = this.world(x, y);
      for (const index of this.candidates([wx - radius, wy - radius, wx + radius, wy + radius])) {
        const [left, top, right, bottom] = this.bounds[index];
        if (Math.hypot(wx - (left + right) / 2, wy - (top + bottom) / 2) <= radius) add(index);
      }
    }
    if (indices.length) this.events.paint(indices, g.tool);
  }

  pointerEnd(event) {
    const g = this.gesture;
    if (!g || g.id !== event.pointerId) return;
    this.gesture = null;
    if (g.tool === "pan") {
      if (event.type === "pointerup" && Math.hypot(g.p[0] - g.origin[0], g.p[1] - g.origin[1]) < 5) {
        const index = this.hit(...g.p);
        if (index >= 0) this.events.inspect(index);
      }
    } else {
      this.events.end();
    }
    this.canvas.classList.remove("dragging");
  }
}
