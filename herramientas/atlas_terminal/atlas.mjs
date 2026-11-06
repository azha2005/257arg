#!/usr/bin/env node
// Visor local original. Lee los HTML generados; no ejecuta sus scripts.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { emitKeypressEvents, createInterface } from 'node:readline';
import { spawn } from 'node:child_process';
import { framePatch } from './screen.mjs';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const ESC = '\x1b[';
const INK = '#e7edf3', MUTED = '#9aaabd', BEIGE = '#e6dcc3';
const alphabet = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
const normalize = s => String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const matches = (text, query) => normalize(query).trim().split(/\s+/).every(word => normalize(text).includes(word));
const plain = s => String(s ?? '').replace(/[\x00-\x1f\x7f-\x9f]/g, ' ');
const num = n => n == null ? 's/d' : Number(n).toLocaleString('es-AR', { maximumFractionDigits: 2 });
const pct = n => n == null ? 's/d' : `${Number(n).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} %`;
const strip = s => s.replace(/\x1b\[[0-9;]*m/g, '');
const clip = (s, w) => s.length > w ? s.slice(0, Math.max(0, w - 1)) + '…' : s;
function clipAnsi(text, width) {
  if (strip(text).length <= width) return text;
  let used = 0, result = '';
  for (const token of text.match(/\x1b\[[0-9;]*m|[^\x1b]/g) || []) {
    if (!token.startsWith('\x1b') && ++used >= width) break;
    result += token;
  }
  return result + '…' + (text.includes('\x1b') ? `${ESC}0m` : '');
}
const rgb = hex => {
  let h = /^#[\da-f]{3,6}$/i.test(hex ?? '') ? hex.slice(1) : '9aaabd';
  if (h.length === 3) h = [...h].map(x => x + x).join('');
  return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
};
const darken = (h, f) => '#' + rgb(h).map(x => Math.round(x * f).toString(16).padStart(2, '0')).join('');
const paint = (h, s, color) => color ? `${ESC}38;2;${rgb(h).join(';')}m${s}${ESC}39m` : s;

export function catalog(root = ROOT) {
  const source = readFileSync(resolve(root, 'sitio/catalogo.py'), 'utf8');
  const entries = [], seen = new Set();
  let group = '';
  const add = (path, year = '', title = '', note = '') => {
    if (seen.has(path) || !existsSync(resolve(root, path)) || /\/index\.html$/.test(path)) return;
    // Estas 18 variantes calculan DATA en el navegador: no son instantáneas JSON.
    if (path.startsWith('mapas/mapa2003escenarios/')) return;
    seen.add(path);
    const stem = basename(path, '.html').replace(/^atlas_/, '');
    const folder = basename(dirname(path));
    let key = folder.startsWith('serieAMBA') ? `amba_${stem}`
      : folder.startsWith('mapa') && !entries.some(e => normalize(e.key) === normalize(folder.slice(4))) ? folder.slice(4) : stem;
    if (entries.some(e => normalize(e.key) === normalize(key))) key = `${folder.replace(/^mapa/, '')}_${stem}`;
    entries.push({ key, path, year: String(year || stem.match(/\d{4}/)?.[0] || ''), title: title || stem.replaceAll('_', ' '), note, group });
  };
  for (const line of source.split(/\r?\n/)) {
    const heading = line.match(/^\s*\("[^"]+",\s*"([^"]+)",\s*"[^"]*",\s*\[/);
    if (heading) group = heading[1];
    const row = line.match(/^\s*\("(mapas\/[^"\n]+\.html)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)/);
    if (row) add(...row.slice(1));
  }
  // Incluye también los atlas enlazados por el catálogo (los índices no llevan DATA).
  const extra = source.match(/\bEXTRA\s*=\s*\[([\s\S]*?)\]/)?.[1] || '';
  group = 'Variantes enlazadas';
  for (const [, pattern] of extra.matchAll(/"(mapas\/[^"\n]+\.html)"/g)) {
    const dir = dirname(pattern), glob = basename(pattern);
    if (!existsSync(resolve(root, dir))) continue;
    const rx = new RegExp('^' + glob.split('*').map(x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$');
    for (const name of readdirSync(resolve(root, dir)).sort()) if (rx.test(name)) add(`${dir.replaceAll('\\', '/')}/${name}`);
  }
  return entries;
}

function jsonObject(source, start) {
  let depth = 0, quoted = false, escaped = false;
  for (let i = start; i < source.length; i++) {
    const c = source[i];
    if (quoted) {
      if (escaped) escaped = false;
      else if (c === '\\') escaped = true;
      else if (c === '"') quoted = false;
    } else if (c === '"') quoted = true;
    else if (c === '{') depth++;
    else if (c === '}' && --depth === 0) return JSON.parse(source.slice(start, i + 1));
  }
  throw new Error('DATA no contiene un objeto JSON completo.');
}

export function ringsFromPath(path) {
  // Los constructores del proyecto emiten polígonos M/L/Z, sin curvas.
  if (/[a-kno-y]/i.test(path.replace(/[eE][+-]?\d+/g, ''))) throw new Error('Geometría SVG con curvas o comandos no admitidos.');
  const tokens = path.match(/[MLZmlz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?/g) || [];
  const rings = [];
  let ring = [], cmd = '', pos = [0, 0];
  for (let i = 0; i < tokens.length;) {
    if (/^[MLZmlz]$/.test(tokens[i])) {
      cmd = tokens[i++];
      if (cmd.toUpperCase() === 'M' && ring.length) { rings.push(ring); ring = []; }
      if (cmd.toUpperCase() === 'Z') { if (ring.length) { pos = ring[0]; rings.push(ring); ring = []; } continue; }
    }
    if (i >= tokens.length) break;
    const x = Number(tokens[i++]), y = Number(tokens[i++]);
    if (!Number.isFinite(x + y) || !/[MLml]/.test(cmd)) throw new Error('Polígono SVG inválido.');
    pos = cmd === cmd.toLowerCase() ? [pos[0] + x, pos[1] + y] : [x, y];
    ring.push(pos);
    if (cmd === 'M') cmd = 'L';
    if (cmd === 'm') cmd = 'l';
  }
  if (ring.length) rings.push(ring);
  return rings.filter(r => r.length >= 3);
}

export function bounds(shapes) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const s of shapes) for (const ring of s.rings) for (const [x, y] of ring) {
    x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
  }
  if (!Number.isFinite(x0 + y0 + x1 + y1)) throw new Error('El atlas no tiene polígonos dibujables.');
  return [x0, y0, Math.max(0.01, x1 - x0), Math.max(0.01, y1 - y0)];
}

export function loadAtlas(entry, root = ROOT) {
  const html = readFileSync(resolve(root, entry.path), 'utf8');
  const marker = /\b(?:const|let|var)\s+DATA\s*=\s*(?=\{)/.exec(html);
  if (!marker) throw new Error(`${entry.path}: no contiene DATA JSON compatible.`);
  const data = jsonObject(html, marker.index + marker[0].length);
  if (!Array.isArray(data.territories) || !data.modes?.some(m => Array.isArray(m.units))) throw new Error('Familia de datos todavía no admitida.');
  const body = html.match(/<g\s+id="B">([\s\S]*?)<g\s+id="frontiers"/)?.[1];
  if (!body) throw new Error('No se encontró la geometría principal #B.');
  const shapes = [];
  for (const [tag] of body.matchAll(/<path\b[^>]*>/g)) {
    const attrs = Object.fromEntries([...tag.matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]]));
    if (attrs['data-i'] == null || !attrs.d) continue;
    if (attrs.transform) throw new Error('Transformación individual de polígono no admitida.');
    const id = Number(attrs['data-i']);
    if (!Number.isInteger(id) || !data.territories[id]) throw new Error('Índice territorial sin ficha.');
    const rings = ringsFromPath(attrs.d);
    if (rings.length) shapes.push({ id, rings });
  }
  // En el SVG nacional la Antártida queda fuera del póster principal: aparece
  // mediante su recuadro. Incluir su geometría remota achicaría todo el país.
  const mainShapes = shapes.filter(s => !/^antartida(?: argentina)?$/.test(normalize(data.territories[s.id].n)));
  const box = bounds(mainShapes.length ? mainShapes : shapes);
  return { entry, data, shapes, box, antarcticaInset: mainShapes.length !== shapes.length };
}

export function rasterize(shapes, box, width, height) {
  const grid = new Int32Array(width * height).fill(-1);
  const [left, top, bw, bh] = box, sx = width / bw, sy = height / bh;
  for (const shape of shapes) {
    let low = Infinity, high = -Infinity;
    for (const ring of shape.rings) for (const [, y] of ring) { low = Math.min(low, y); high = Math.max(high, y); }
    const begin = Math.max(0, Math.ceil((low - top) * sy - 0.5));
    const end = Math.min(height, Math.ceil((high - top) * sy - 0.5));
    for (let row = begin; row < end; row++) {
      const y = top + (row + 0.5) / sy, hits = [];
      for (const ring of shape.rings) for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
        const a = ring[j], b = ring[i];
        if ((a[1] > y) !== (b[1] > y)) hits.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]));
      }
      hits.sort((a, b) => a - b);
      for (let i = 0; i + 1 < hits.length; i += 2) {
        const x0 = Math.min(width, Math.max(0, Math.ceil((hits[i] - left) * sx - 0.5)));
        const x1 = Math.min(width, Math.max(0, Math.ceil((hits[i + 1] - left) * sx - 0.5)));
        if (x1 > x0) grid.fill(shape.id, row * width + x0, row * width + x1);
      }
    }
  }
  return grid;
}

export function modeOf(atlas, id) {
  const mode = id == null ? atlas.data.modes[0] : atlas.data.modes.find(m => m.id === id);
  if (!mode) throw new Error(`Modo desconocido: ${id}. Disponibles: ${atlas.data.modes.map(m => m.id).join(', ')}`);
  return mode;
}
export function recordFor(atlas, mode, id) {
  const p = atlas.data.territories[id]?.p;
  if (atlas.data.solid?.includes(p) && !atlas.data.solidExcept?.includes(id)) return mode.prov?.[p] || mode.units[id];
  return mode.units[id];
}
export function fillFor(atlas, mode, id) {
  const rec = recordFor(atlas, mode, id);
  // GANÓ usa color plano declarado. Las coropletas conservan el fill del HTML.
  return rec?.fill || atlas.data.candidates[rec?.w]?.base || BEIGE;
}
export function provinceRecord(atlas, mode, id) {
  const territory = atlas.data.territories[id];
  if (!territory) return undefined;
  // Las islas mantienen su reserva propia aunque su provincia tenga ganador.
  if (/^islas malvinas$/i.test(territory.n)) return mode.units[id];
  return mode.prov?.[territory.p];
}
export function provinceFill(atlas, mode, id) {
  const rec = provinceRecord(atlas, mode, id);
  return rec?.fill || atlas.data.candidates[rec?.w]?.base || BEIGE;
}
export function halfBlock(top, bottom) {
  // 49 recupera el fondo de la terminal. No pinta rectángulos fuera del país.
  if (!top && !bottom) return `${ESC}49m `;
  if (!top) return `${ESC}49m${ESC}38;2;${rgb(bottom).join(';')}m▄`;
  return `${ESC}38;2;${rgb(top).join(';')}m${bottom ? `${ESC}48;2;${rgb(bottom).join(';')}m` : `${ESC}49m`}▀`;
}
const candidateName = (a, code) => plain(a.data.candidates[code]?.n || code);
const special = (atlas, row) => /(?:^|_)(BLA|NUL|IMP|REC|OTR)$/.test(row[0]) || /^(en blanco|votos en blanco|nulos|anulados|observados|recurridos|otros)\b/i.test(candidateName(atlas, row[0]));
export function closest(atlas) {
  const mode = atlas.data.modes.find(m => m.id === 'gan') || atlas.data.modes[0];
  return mode.units.flatMap((r, id) => {
    if (!r?.w || r.fill || atlas.data.solid?.includes(atlas.data.territories[id]?.p)) return [];
    const lines = (r.lines || []).filter(row => !special(atlas, row) && Number.isFinite(row[2])).sort((a, b) => b[2] - a[2]);
    if (lines.length < 2) return [];
    return [{ id, gap: lines[0][2] - lines[1][2], lines: lines.slice(0, 2) }];
  }).sort((a, b) => a.gap - b.gap || a.id - b.id);
}
function wrap(text, width) {
  const out = [];
  for (const para of plain(text).split(/\n/)) {
    let line = '';
    for (const word of para.split(/\s+/)) {
      if (line && line.length + word.length + 1 > width) { out.push(line); line = ''; }
      line += (line ? ' ' : '') + word;
    }
    if (line) out.push(line);
  }
  return out;
}
const territoryName = (atlas, id) => {
  const t = atlas.data.territories[id];
  return `${t.n} · ${t.p}`;
};

function recordLines(atlas, rec, width, color) {
  if (!rec) return ['Sin ficha disponible.'];
  const out = [];
  for (const [code, votes, percent] of rec.lines || []) {
    out.push(paint(atlas.data.candidates[code]?.base || MUTED, clip(candidateName(atlas, code), width), color));
    out.push(`  ${num(votes)} votos · ${pct(percent)}`);
  }
  out.push('');
  for (const [k, v] of rec.metrics || []) out.push(...wrap(`${k}: ${v}`, width));
  if (rec.note) out.push('', ...wrap(rec.note, width));
  return out;
}
function nationalLines(atlas, mode, width, color) {
  const n = mode.national || {}, out = [];
  for (const c of n.cands || []) {
    const base = atlas.data.candidates[c.code]?.base || MUTED;
    out.push(paint(base, clip(candidateName(atlas, c.code), width), color));
    out.push(`  ${pct(c.pct)} · ${num(c.votes)} votos`);
    const w = Math.max(1, Math.floor((width - 2) * Math.min(100, c.pct || 0) / 100));
    out.push(paint(base, '  ' + '━'.repeat(w), color));
  }
  out.push('');
  for (const [k, v] of n.metrics || []) out.push(...wrap(`${k}: ${v}`, width));
  out.push('', ...wrap('Resultado del cartel del atlas. No se recalcula sumando las unidades del mapa.', width));
  return out;
}
function currentBox(state) {
  const { atlas, province, inset, zoom } = state;
  let box = atlas.box;
  if (province) {
    const shapes = atlas.shapes.filter(s => atlas.data.territories[s.id].p === province && !/^antartida(?: argentina)?$/.test(normalize(atlas.data.territories[s.id].n)));
    if (shapes.length) box = bounds(shapes);
  }
  if (inset >= 0 && atlas.data.insets?.[inset]) box = atlas.data.insets[inset].win;
  const [x, y, w, h] = box;
  return [x + w / 2 - w / zoom / 2 + state.panX * w, y + h / 2 - h / zoom / 2 + state.panY * h, w / zoom, h / zoom];
}
export function makeState(atlas, options = {}) {
  const { mode, ...rest } = options;
  return { atlas, mode: modeOf(atlas, mode), cellAspect: 2, selected: null, view: options.province ? 'province' : 'map', level: options.province || options.selected != null ? 'units' : 'provinces', detailProvince: options.province || '', scroll: 0, query: '', editing: false, province: options.province || '', inset: -1, zoom: 1, panX: 0, panY: 0, cursor: 0, message: '', ...rest };
}
function overview(state) {
  Object.assign(state, { province: '', detailProvince: '', level: 'provinces', inset: -1, zoom: 1, panX: 0, panY: 0, selected: null, view: 'map', scroll: 0 });
}
export function focusProvince(state, province) {
  Object.assign(state, { province, detailProvince: province, level: 'units', inset: -1, zoom: 1, panX: 0, panY: 0, selected: null, view: 'province', scroll: 0 });
  state.rasterKey = '';
}
export function handleMapClick(state, column, row) {
  if (!state.hit) return false;
  const { x, y, width: w, height: h } = state.hit;
  const cx = column - x, cy = (row - y) * 2;
  if (cx < 0 || cx >= w || cy < 0 || cy >= h) return false;
  const a = state.grid[cy * w + cx], b = state.grid[(cy + 1) * w + cx];
  const id = a >= 0 ? a : b;
  if (id < 0) return false;
  if (state.level === 'provinces') focusProvince(state, state.atlas.data.territories[id].p);
  else { state.selected = id; state.view = 'map'; state.scroll = 0; }
  return true;
}
export function focusMetro(state, capital = false) {
  const insets = state.atlas.data.insets || [];
  const index = insets.findIndex(i => capital ? i.id === 'caba' || /capital federal|ciudad de buenos aires/i.test(i.label)
    : ['gba', 'core'].includes(i.id) || /metropolitana|conurbano/i.test(i.label));
  if (index < 0) { state.message = 'Este atlas no tiene ese recuadro. Usá la búsqueda de unidades (/).'; return; }
  const province = capital ? state.atlas.data.territories.find(t => /^(capital federal|ciudad de buenos aires)$/i.test(t.p))?.p || '' : '';
  Object.assign(state, { inset: index, level: 'units', province, detailProvince: province, zoom: 1, panX: 0, panY: 0, selected: null, view: province ? 'province' : 'map', scroll: 0, editing: false });
}
function listItems(state) {
  const { atlas, mode } = state;
  if (state.view === 'search') return searchIds(state).map(id => ({ id, label: territoryName(atlas, id) }));
  if (state.view === 'closest') return closest(atlas).map(r => ({ id: r.id, label: `${num(r.gap)} pp · ${territoryName(atlas, r.id)}` }));
  if (state.view === 'provinces') return Object.keys(mode.prov || {}).sort((a, b) => a.localeCompare(b, 'es')).map(p => ({ province: p, label: p }));
  if (state.view === 'catalog') return (state.entries || []).filter(e => matches(`${e.key} ${e.year} ${e.title} ${e.group.replace(/\d{4}/g, '')}`, state.query))
    .map(entry => ({ entry, label: `${entry.key} · ${entry.year} · ${entry.title}` }));
  return [];
}
function activateItem(state) {
  const items = listItems(state);
  state.cursor = Math.max(0, Math.min(state.cursor, items.length - 1));
  const item = items[state.cursor];
  if (!item) { state.message = 'Sin coincidencias. Cambiá el texto para filtrar.'; return; }
  state.editing = false;
  if (item.entry) return item.entry;
  if (item.province) focusProvince(state, item.province);
  if (item.id != null) { focusProvince(state, state.atlas.data.territories[item.id].p); state.selected = item.id; state.view = 'map'; }
  state.scroll = 0;
}
export function handleClick(state, column, row) {
  const button = state.buttons?.find(b => row === b.y && column >= b.x && column < b.x + b.width);
  if (button) { state.editing = false; return handleKey(state, button.key, { name: button.key }); }
  const panel = state.panelHit;
  if (panel && column >= panel.x && column < panel.x + panel.width && row >= panel.y && row < panel.y + panel.height) {
    const index = row - panel.y + panel.offset;
    if (index >= listItems(state).length) return false;
    state.cursor = index;
    return activateItem(state) || true;
  }
  return handleMapClick(state, column, row);
}
function searchIds(state) {
  return state.atlas.data.territories.flatMap((t, i) => matches(`${t.n} ${t.p}`, state.query) ? [i] : []);
}
function sidePanel(state, width, color) {
  const { atlas, mode, selected } = state;
  let title, lines, items = [];
  if (state.view === 'search') {
    title = `BUSCAR: ${state.query}${state.editing ? ' _' : ''}`;
    items = listItems(state);
  } else if (state.view === 'closest') {
    title = 'MÁS AJUSTADAS · puntos porcentuales';
    items = listItems(state);
  } else if (state.view === 'provinces') {
    title = 'PROVINCIAS · fichas del atlas';
    items = listItems(state);
  } else if (state.view === 'catalog') {
    title = `ATLAS LOCALES: ${state.query}${state.editing ? ' _' : ''}`;
    items = listItems(state);
  } else if (state.view === 'notes') {
    title = 'FUENTES Y RESERVAS';
    lines = [atlas.entry.path, '', ...wrap(mode.note || 'Ver las fuentes en el atlas HTML.', width)];
    if (atlas.entry.note) lines.push('', ...wrap(atlas.entry.note, width));
  } else if (state.view === 'province') {
    title = state.detailProvince;
    lines = recordLines(atlas, mode.prov?.[state.detailProvince], width, color);
    lines.push('', ...wrap('Ficha provincial tomada del atlas; puede tener una cobertura diferente de las unidades con geometría.', width));
  } else if (selected != null) {
    title = territoryName(atlas, selected);
    lines = recordLines(atlas, mode.units[selected], width, color);
  } else {
    title = /amba|provincia de buenos aires/i.test(atlas.data.title) ? 'RESULTADO DEL ÁREA DEL ATLAS' : 'RESULTADO NACIONAL DEL ATLAS';
    lines = nationalLines(atlas, mode, width, color);
  }
  state.items = items;
  if (['search', 'closest', 'provinces', 'catalog'].includes(state.view)) {
    state.cursor = Math.max(0, Math.min(state.cursor, items.length - 1));
    lines = items.map((item, i) => paint(i === state.cursor ? '#ffda79' : INK, `${i === state.cursor ? '›' : ' '} ${clip(item.label, width - 2)}`, color));
    if (!items.length) lines = ['Sin coincidencias.'];
  }
  return [paint('#ffda79', clip(plain(title), width), color), '', ...(lines || [])];
}

export function render(state, width = 120, height = 42, color = true) {
  width = Math.max(60, Math.min(240, width)); height = Math.max(18, Math.min(100, height));
  const { atlas, mode } = state, rows = height - 9, box = currentBox(state);
  const mapArea = Math.max(22, Math.floor(width * 0.47)), panelWidth = width - mapArea - 4;
  // Mantener la relación física X/Y del SVG incluso cuando medio carácter
  // no es un cuadrado. La consola de Windows informa su celda real.
  const aspect = state.cellAspect || 2;
  const scale = Math.min((mapArea - 2) / box[2], rows * aspect / box[3]);
  const mw = Math.max(2, Math.floor(box[2] * scale));
  const mh = Math.max(2, Math.floor(box[3] * scale / aspect) * 2);
  const cacheKey = `${mw}:${mh}:${box.join(',')}:${state.province}`;
  if (state.rasterKey !== cacheKey) {
    const shapes = state.province ? atlas.shapes.filter(s => atlas.data.territories[s.id].p === state.province) : atlas.shapes;
    state.grid = rasterize(shapes, box, mw, mh); state.rasterKey = cacheKey;
  }
  const grid = state.grid, offset = Math.floor((mapArea - mw) / 2);
  state.hit = { width: mw, height: mh, x: offset + 1, y: 4, box };
  const first = atlas.data.modes.find(m => m.id === 'gan') || atlas.data.modes[0];
  const records = state.level === 'provinces' ? Object.values(first.prov || {})
    : atlas.shapes.filter(s => !state.province || atlas.data.territories[s.id].p === state.province).map(s => first.units[s.id]);
  const winners = [...new Set(records.map(r => r?.w).filter(Boolean))];
  const symbols = new Map(winners.map((w, i) => [w, alphabet[i] || '*']));
  const estimated = /estimad|estimaci[oó]n|hip[oó]tesis|hipot[eé]tico|simulaci[oó]n|contrafactual|ucron[ií]a/i.test(`${atlas.entry.note} ${mode.note}`);
  const lines = [paint('#ffda79', clip(`ATLAS ARGENTINOS / ${atlas.entry.key} / ${atlas.data.year}${estimated ? ' / ESTIMACIÓN O ESCENARIO' : ''}`, width), color),
    clip(plain(`${atlas.data.title} ${atlas.data.year} · ${mode.tile || mode.id}${mode.id === 'gan' ? ' (color plano)' : !color ? ' (símbolos de ganador)' : ''}`), width),
    paint(MUTED, clip(`${atlas.entry.note || Object.values(atlas.data.sets || {})[0]?.subtitle || ''} · ${state.level === 'provinces' ? 'Por provincia · clic para ampliar' : (state.inset >= 0 ? atlas.data.insets[state.inset]?.label : state.province) || 'Unidades locales'}`, width), color)];
  const panel = sidePanel(state, panelWidth, color);
  const list = ['search', 'closest', 'catalog', 'provinces'].includes(state.view);
  if (list) {
    if (state.cursor < state.scroll) state.scroll = state.cursor;
    if (state.cursor >= state.scroll + rows - 2) state.scroll = state.cursor - rows + 3;
  }
  state.maxScroll = Math.max(0, panel.length - rows);
  state.scroll = Math.max(0, Math.min(state.scroll, state.maxScroll));
  state.panelHit = list ? { x: mapArea + 4, y: 6, width: panelWidth, height: rows - 2, offset: state.scroll } : null;
  const visiblePanel = [...panel.slice(0, 2), ...panel.slice(2 + state.scroll, rows + state.scroll)];
  const colorCache = new Map();
  const identity = id => id < 0 ? null : state.level === 'provinces' ? atlas.data.territories[id].p : id;
  const at = (x, y) => {
    const id = grid[y * mw + x];
    if (id < 0) return null;
    if (!colorCache.has(id)) colorCache.set(id, state.level === 'provinces' ? provinceFill(atlas, mode, id) : fillFor(atlas, mode, id));
    let base = colorCache.get(id);
    if (state.selected === id) base = '#fff3ad';
    else if ((x > 0 && identity(grid[y * mw + x - 1]) !== identity(id)) || (y > 0 && identity(grid[(y - 1) * mw + x]) !== identity(id))) base = darken(base, 0.6);
    return base;
  };
  for (let row = 0; row < rows; row++) {
    let map = ' '.repeat(offset);
    if (row < mh / 2) for (let x = 0; x < mw; x++) {
      if (color) map += halfBlock(at(x, row * 2), at(x, row * 2 + 1));
      else {
        const id = grid[row * 2 * mw + x] >= 0 ? grid[row * 2 * mw + x] : grid[(row * 2 + 1) * mw + x];
        const r = state.level === 'provinces' ? provinceRecord(atlas, first, id) : recordFor(atlas, first, id);
        map += id < 0 ? ' ' : state.selected === id ? '@' : symbols.get(r?.w) || '.';
      }
    }
    if (color) map += `${ESC}0m`;
    const visible = strip(map).length;
    lines.push(map + ' '.repeat(Math.max(0, mapArea - visible)) + ' │ ' + clipAnsi(visiblePanel[row] || '', panelWidth));
  }
  const legend = winners.map(w => paint(atlas.data.candidates[w]?.base || MUTED, `${symbols.get(w)} ${candidateName(atlas, w)}`, color)).join(' · ');
  // Recorta sin romper secuencias ANSI.
  let used = 0, shortLegend = '';
  for (const chunk of legend.match(/\x1b\[[0-9;]*m|[^\x1b]/g) || []) {
    if (!chunk.startsWith('\x1b') && ++used > width - 2) break;
    shortLegend += chunk;
  }
  lines.push(shortLegend + (color ? `${ESC}0m` : ''));
  const controls = [['a', 'Atlas'], ['b', 'AMBA'], ['d', 'Capital'], ['m', 'Modo'], ['n', 'País'], ['p', 'Provincias'], ['c', 'Ajustadas'], ['/', 'Buscar'], ['f', 'Fuentes']];
  let toolbar = '';
  state.buttons = controls.map(([key, label]) => {
    const text = `${key} ${label}`, x = toolbar.length + 1;
    toolbar += text + ' · ';
    return { x, y: lines.length + 1, width: Math.max(0, Math.min(text.length, width - x)), key };
  });
  lines.push(paint(MUTED, clip(toolbar.slice(0, -3), width), color));
  lines.push(paint(MUTED, clip('↑↓ / j k Lista · Enter Ficha · i Recuadros · +− Zoom · HJKL Mover · r Restablecer', width), color));
  lines.push(paint(MUTED, clip('o Abrir HTML · Esc Volver · q Salir · [ ] Atlas anterior/siguiente · Av/RePág Desplazar', width), color));
  lines.push(paint('#ffda79', clip(state.message || (list ? 'Escribí para filtrar · ↑↓ elegir · Enter o clic: abrir · Esc: volver' : state.level === 'provinces' ? 'Clic en provincia: ampliar · b: AMBA · d: Capital · Sin dato: beige / .' : 'Clic en unidad: ficha · + / −: zoom · b: AMBA · d: Capital · Esc: volver'), width), color));
  return lines.join('\n');
}

function help() {
  return `Atlas argentinos en la terminal · Node 18 o posterior · sin dependencias\n\nnode herramientas/atlas_terminal/atlas.mjs [atlas] [opciones]\n\n  --list                 Catálogo local (incluye variantes enlazadas)\n  --print                Imprimir y salir; automático si la salida no es terminal\n  --color / --no-color   ANSI RGB / mapa con símbolos\n  --mode ID              Modo del HTML (gan, par, ucr, etc.)\n  --view VISTA           map, closest, provinces, notes\n  --search TEXTO         Buscar unidades; con --print imprime sus fichas\n  --province PROVINCIA   Acercar una provincia por nombre exacto\n  --aspect N             Relación alto/ancho de celda; Windows la detecta al abrir\n  --width N --height N   Tamaño de impresión (60–240 × 18–100)\n  --json                 Datos de la vista: conserva cifras y notas, omite imágenes\n\nEjemplos:\n  node herramientas/atlas_terminal/atlas.mjs 2023bal\n  node herramientas/atlas_terminal/atlas.mjs 1918 --search Jujuy --print\n  node herramientas/atlas_terminal/atlas.mjs 2025 --view closest --print\n\nGANÓ se representa en color plano; las demás vistas usan el fill del HTML.\nLas diferencias locales son entre las dos primeras filas partidarias con\nporcentajes publicados. No son pronósticos ni un cálculo de bancas.\n`;
}
export function parseArgs(args) {
  const options = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (['--help', '-h'].includes(arg)) options.help = true;
    else if (['--list', '--print', '--json'].includes(arg)) options[arg.slice(2)] = true;
    else if (arg === '--color') options.color = true;
    else if (arg === '--no-color') options.color = false;
    else if (['--atlas', '--mode', '--view', '--search', '--province', '--width', '--height', '--aspect'].includes(arg)) {
      if (!args[i + 1] || args[i + 1].startsWith('--')) throw new Error(`Falta el valor de ${arg}.`);
      options[arg.slice(2)] = args[++i];
    } else if (!arg.startsWith('-') && !options.atlas) options.atlas = arg;
    else throw new Error(`Argumento desconocido: ${arg}`);
  }
  for (const k of ['width', 'height']) if (options[k] != null && (!/^\d+$/.test(options[k]) || Number(options[k]) < 1)) throw new Error(`${k}: se necesita un entero positivo.`);
  if (options.aspect != null && (!Number.isFinite(Number(options.aspect)) || Number(options.aspect) < 0.5 || Number(options.aspect) > 4)) throw new Error('aspect: se necesita la relación alto/ancho de celda, entre 0.5 y 4.');
  if (options.view && !['map', 'closest', 'provinces', 'notes'].includes(options.view)) throw new Error('Vista desconocida. Usar map, closest, provinces o notes.');
  return options;
}
export function resolveEntry(entries, key) {
  if (!key) return entries.find(e => e.key === '2023bal') || entries[0];
  const exact = entries.find(e => normalize(e.key) === normalize(key) || normalize(e.path) === normalize(key));
  if (exact) return exact;
  const matches = entries.filter(e => normalize(`${e.key} ${e.title} ${e.year}`).includes(normalize(key)));
  if (matches.length === 1) return matches[0];
  throw new Error(matches.length ? `Atlas ambiguo: ${matches.map(e => e.key).join(', ')}. Elegí una clave.` : `No se encontró ${key}. Usá --list.`);
}
function openHtml(atlas) {
  const path = resolve(ROOT, atlas.entry.path);
  const [exe, args] = process.platform === 'win32' ? ['explorer.exe', [path]] : process.platform === 'darwin' ? ['open', [path]] : ['xdg-open', [path]];
  const child = spawn(exe, args, { stdio: 'ignore', detached: true, windowsHide: true });
  child.on('error', () => {}); child.unref();
}
function nativeConsoleMouse(onClick, onFont) {
  if (process.platform !== 'win32' || process.env.WT_SESSION) return null;
  const source = resolve(dirname(fileURLToPath(import.meta.url)), 'ConsoleMouse.cs').replaceAll("'", "''");
  const command = `$ErrorActionPreference='Stop'; Add-Type -Path '${source}'; [AtlasConsoleMouse]::Run(${process.pid})`;
  const child = spawn('powershell.exe', ['-NoProfile', '-NonInteractive', '-EncodedCommand', Buffer.from(command, 'utf16le').toString('base64')], { windowsHide: true, stdio: ['ignore', 'pipe', 'ignore'] });
  child.on('error', () => {});
  const lines = createInterface({ input: child.stdout });
  lines.on('line', line => {
    const match = /^(\d+);(\d+)$/.exec(line);
    if (match) onClick(Number(match[1]), Number(match[2]));
    const font = /^font;(\d+);(\d+)$/.exec(line);
    if (font && Number(font[1]) > 0 && Number(font[2]) > 0) onFont(Number(font[2]) / Number(font[1]));
  });
  return child;
}
export function handleKey(state, text, key = {}) {
  state.message = '';
  if (key.ctrl && key.name === 'c') return 'quit';
  if (state.editing) {
    if (key.name === 'escape') { state.editing = false; state.query = ''; state.view = 'map'; }
    else if (key.name === 'return') return activateItem(state);
    else if (['up', 'down', 'pageup', 'pagedown', 'home', 'end'].includes(key.name)) {
      const count = listItems(state).length;
      state.cursor = key.name === 'home' ? 0 : key.name === 'end' ? count - 1
        : Math.max(0, Math.min(count - 1, state.cursor + ({ up: -1, down: 1, pageup: -10, pagedown: 10 })[key.name]));
      return;
    } else if (key.name === 'backspace') { state.query = state.query.slice(0, -1); state.cursor = state.scroll = 0; }
    else if (text && !key.ctrl && !key.meta && !/[\x00-\x1f\x7f]/.test(text)) { state.query += text; state.cursor = state.scroll = 0; }
    return;
  }
  const list = ['catalog', 'search', 'closest', 'provinces'].includes(state.view);
  if (text === 'q') return 'quit';
  if (text === '[' || text === ']') return text === '[' ? 'previous' : 'next';
  if (text === 'o') { openHtml(state.atlas); state.message = 'Abriendo el atlas HTML local.'; return; }
  if (text === 'a' || text === '/') {
    state.view = text === 'a' ? 'catalog' : 'search'; state.query = ''; state.editing = true; state.scroll = 0;
    state.cursor = text === 'a' ? Math.max(0, (state.entries || []).findIndex(e => e.path === state.atlas.entry.path)) : 0;
    state.scroll = Math.max(0, state.cursor - 8);
    return;
  }
  if (text === 'b' || text === 'd') { focusMetro(state, text === 'd'); return; }
  if (text === 'm') { const modes = state.atlas.data.modes; state.mode = modes[(modes.indexOf(state.mode) + 1) % modes.length]; return; }
  if (text === 'n' || text === 'r') { overview(state); return; }
  if (['c', 'p', 'f'].includes(text)) { state.view = ({ c: 'closest', p: 'provinces', f: 'notes' })[text]; state.selected = null; state.scroll = 0; state.cursor = 0; return; }
  if (key.name === 'escape') {
    if (state.selected != null) { state.selected = null; state.view = state.province ? 'province' : 'map'; state.scroll = 0; }
    else overview(state);
    return;
  }
  if (text === 'i') {
    state.inset = (state.inset + 2) % ((state.atlas.data.insets?.length || 0) + 1) - 1;
    state.level = state.inset >= 0 ? 'units' : 'provinces'; state.province = ''; state.zoom = 1; state.panX = state.panY = 0; state.selected = null; state.view = 'map'; return;
  }
  if (['+', '=', '-'].includes(text)) { state.zoom = Math.max(1, Math.min(64, state.zoom * (text === '-' ? 1 / 1.5 : 1.5))); return; }
  if (['H', 'J', 'K', 'L'].includes(text)) { const step = .15 / state.zoom; state.panX += text === 'H' ? -step : text === 'L' ? step : 0; state.panY += text === 'K' ? -step : text === 'J' ? step : 0; return; }
  if (key.name === 'down' || text === 'j') { if (list) state.cursor++; else state.scroll++; return; }
  if (key.name === 'up' || text === 'k') { if (list) state.cursor--; else state.scroll--; return; }
  if (key.name === 'pagedown') { if (list) state.cursor += 10; else state.scroll += 10; return; }
  if (key.name === 'pageup') { if (list) state.cursor -= 10; else state.scroll -= 10; return; }
  if (key.name === 'return' && list) {
    return activateItem(state);
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) { console.log(help()); return; }
  const entries = catalog();
  if (options.list) { for (const e of entries) console.log(`${e.key.padEnd(29)} ${e.year} ${e.title}${e.note ? ' · ' + e.note : ''}`); return; }
  let cellAspect = Number(options.aspect || 2);
  let state = makeState(loadAtlas(resolveEntry(entries, options.atlas)), { entries, mode: options.mode, view: options.view || 'map', province: options.province || '', cellAspect });
  if (state.province && !options.view) state.view = 'province';
  if (state.province && !state.atlas.data.territories.some(t => t.p === state.province)) throw new Error('Provincia desconocida. El nombre debe coincidir con la ficha del atlas.');
  if (options.search != null) { state.query = options.search; state.view = 'search'; }
  const color = options.color ?? Boolean(process.stdout.isTTY && !process.env.NO_COLOR);
  const width = Number(options.width || process.stdout.columns || 120), height = Number(options.height || process.stdout.rows || 42);
  if (options.json) {
    const ids = options.search == null ? state.atlas.data.territories.map((_, i) => i) : searchIds(state);
    console.log(JSON.stringify({ atlas: state.atlas.entry, mode: state.mode.id, note: state.mode.note, national: state.mode.national, provinces: state.mode.prov,
      units: ids.map(i => ({ id: i, territory: state.atlas.data.territories[i], ...state.mode.units[i] })),
      candidates: Object.fromEntries(Object.entries(state.atlas.data.candidates).map(([k, { img, ...v }]) => [k, v])) }, null, 2)); return;
  }
  if (options.print || !process.stdout.isTTY || !process.stdin.isTTY) {
    if (options.search != null) {
      const ids = searchIds(state);
      console.log(`${state.atlas.data.title} ${state.atlas.data.year}\n${plain(state.mode.note)}\n`);
      for (const id of ids) console.log(territoryName(state.atlas, id) + '\n' + recordLines(state.atlas, state.mode.units[id], width, color).join('\n') + '\n');
      if (!ids.length) console.log('Sin coincidencias.');
    } else console.log(render(state, width, height, color));
    return;
  }
  emitKeypressEvents(process.stdin);
  process.stdin.setRawMode(true); process.stdin.resume();
  let cleaned = false;
  let nativeMouse = null;
  let drawTimer = null, previous = [];
  const cleanup = () => {
    if (cleaned) return; cleaned = true;
    clearTimeout(drawTimer);
    nativeMouse?.kill();
    process.stdout.write(`${ESC}?1000l${ESC}?1006l${ESC}?7h${ESC}?25h${ESC}0m${ESC}?1049l`);
    process.stdin.setRawMode(false); process.stdin.pause();
  };
  const paintFrame = () => {
    drawTimer = null;
    const columns = Math.max(60, (process.stdout.columns || 80) - 2), rows = process.stdout.rows || 24;
    const next = render(state, columns, rows, color).split('\n');
    const patch = framePatch(previous, next, columns, rows);
    if (patch) process.stdout.write(patch);
    previous = next;
  };
  const draw = () => { if (!drawTimer && !cleaned) drawTimer = setTimeout(paintFrame, 16); };
  const switchAtlas = entry => {
    try { state = makeState(loadAtlas(entry), { entries, cellAspect }); }
    catch (error) { state.message = error.message; }
  };
  let lastClick = null;
  const click = (x, y, source) => {
    if (lastClick && lastClick.source !== source && lastClick.x === x && lastClick.y === y && Date.now() - lastClick.at < 250) return;
    lastClick = { x, y, source, at: Date.now() };
    const result = handleClick(state, x, y);
    if (result?.path) switchAtlas(result);
    if (result !== false) draw();
  };
  process.stdout.write(`${ESC}?1049h${ESC}?25l${ESC}?1000h${ESC}?1006h${ESC}?7l`);
  process.on('exit', cleanup);
  process.once('SIGINT', () => { cleanup(); process.exit(0); });
  process.stdout.on('resize', () => { previous = []; draw(); });
  // readline ve el mismo flujo: se ignoran sus eventos keypress para paquetes de ratón.
  let mouseChunk = false;
  process.stdin.prependListener('data', chunk => {
    const text = chunk.toString(); mouseChunk = /\x1b\[</.test(text);
    if (!mouseChunk) return;
    for (const m of text.matchAll(/\x1b\[<(\d+);(\d+);(\d+)([Mm])/g)) {
      if (m[4] !== 'M' || !state.hit) continue;
      if (Number(m[1]) === 0) click(Number(m[2]), Number(m[3]), 'sgr');
      else if ([64, 65].includes(Number(m[1]))) {
        handleKey(state, '', { name: Number(m[1]) === 64 ? 'up' : 'down' }); draw();
      }
    }
  });
  process.stdin.on('keypress', (text, key) => {
    if (mouseChunk) return;
    try {
      const result = handleKey(state, text, key);
      if (result === 'quit') { cleanup(); process.exit(0); }
      else if (result === 'previous' || result === 'next') switchAtlas(entries[(entries.findIndex(e => e.path === state.atlas.entry.path) + (result === 'next' ? 1 : -1) + entries.length) % entries.length]);
      else if (result?.path) switchAtlas(result);
      draw();
    } catch (error) { state.message = error.message; draw(); }
  });
  if (!options.atlas) handleKey(state, 'a', { name: 'a' });
  try {
    paintFrame();
    nativeMouse = nativeConsoleMouse((x, y) => click(x, y, 'native'), aspect => {
      if (options.aspect != null || aspect < 0.5 || aspect > 4 || Math.abs(aspect - cellAspect) < 0.001) return;
      cellAspect = state.cellAspect = aspect; draw();
    });
  } catch (error) { cleanup(); throw error; }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(`Atlas terminal: ${error.message}`); process.exitCode = 1; });
}
