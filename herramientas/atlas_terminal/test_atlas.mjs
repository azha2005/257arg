import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { ROOT, catalog, resolveEntry, loadAtlas, modeOf, ringsFromPath, rasterize, fillFor, recordFor, provinceFill, halfBlock, handleMapClick, handleClick, closest, makeState, render, handleKey, parseArgs } from './atlas.mjs';
import { cells, framePatch } from './screen.mjs';

const entries = catalog();
const get = key => loadAtlas(resolveEntry(entries, key));
const bal = get('2023bal');

test('catálogo: claves únicas y variantes enlazadas; excluye páginas índice', () => {
  assert.ok(entries.length > 100);
  assert.equal(new Set(entries.map(e => e.key)).size, entries.length);
  assert.ok(entries.some(e => e.path.includes('mapa2003alt/atlas_')));
  assert.ok(!entries.some(e => e.path.endsWith('/index.html')));
  assert.throws(() => resolveEntry(entries, 'presidente'), /ambiguo/);
});

test('lee cifras nacionales sin sumar ni cambiar las fichas locales', () => {
  const mode = modeOf(bal, 'gan');
  assert.equal(mode.national.cands.find(c => c.code === 'LLA').votes, 14554560);
  const id = bal.data.territories.findIndex(t => t.n === '25 de Mayo' && t.p === 'Buenos Aires');
  assert.deepEqual(mode.units[id].lines[0], ['LLA', 14530, 63.72]);
  assert.equal(fillFor(bal, mode, id), bal.data.candidates.LLA.base);
  assert.equal(fillFor(bal, modeOf(bal, 'lla'), id), '#160f1e');
});

test('vista inicial: Buenos Aires usa su ganador provincial, no el de cada partido', () => {
  const mode = modeOf(bal, 'gan');
  const id = bal.data.territories.findIndex(t => t.n === '25 de Mayo' && t.p === 'Buenos Aires');
  assert.equal(mode.units[id].w, 'LLA');
  assert.equal(mode.prov['Buenos Aires'].w, 'UP');
  assert.equal(provinceFill(bal, mode, id), bal.data.candidates.UP.base);
  assert.equal(makeState(bal).level, 'provinces');
  const malvinas = bal.data.territories.findIndex(t => t.n === 'Islas Malvinas');
  assert.equal(provinceFill(bal, mode, malvinas), '#a9a9a9');
});

test('fondo: celdas vacías y medias celdas usan el fondo de la terminal', () => {
  assert.equal(halfBlock(null, null), '\x1b[49m ');
  assert.ok(!halfBlock('#123456', null).includes('48;2;'));
  assert.ok(!halfBlock(null, '#123456').includes('48;2;'));
  assert.ok(halfBlock(null, '#123456').endsWith('▄'));
  assert.ok(halfBlock('#123456', '#abcdef').includes('48;2;171;205;239'));
  assert.ok(!render(makeState(bal), 120, 42, true).includes('48;2;16;24;32'));
});

function mapCoordinate(state, accepts) {
  const { width, height, x, y } = state.hit;
  for (let row = 0; row < height; row += 2) for (let col = 0; col < width; col++) {
    const a = state.grid[row * width + col], b = state.grid[(row + 1) * width + col];
    const id = a >= 0 ? a : b;
    if (id >= 0 && accepts(id)) return [x + col, y + row / 2];
  }
  throw new Error('No se encontró el área buscada en el mapa.');
}

test('clic: provincia → ampliación local → ficha → volver a provincia → país', () => {
  const state = makeState(bal, { entries });
  render(state, 120, 42, true);
  const countryBox = state.hit.box;
  const coord = mapCoordinate(state, id => bal.data.territories[id].p === 'Buenos Aires');
  assert.ok(handleMapClick(state, ...coord));
  assert.equal(state.province, 'Buenos Aires');
  assert.equal(state.level, 'units');
  assert.equal(state.view, 'province');
  render(state, 120, 42, true);
  assert.ok(state.hit.box[2] < countryBox[2]);
  assert.ok(state.hit.box[3] < countryBox[3]);
  assert.ok([...state.grid].every(id => id < 0 || bal.data.territories[id].p === 'Buenos Aires'));
  assert.ok(handleMapClick(state, ...mapCoordinate(state, () => true)));
  assert.equal(state.view, 'map');
  assert.equal(bal.data.territories[state.selected].p, 'Buenos Aires');
  handleKey(state, '', { name: 'escape' });
  assert.equal(state.selected, null);
  assert.equal(state.view, 'province');
  handleKey(state, '', { name: 'escape' });
  assert.equal(state.province, '');
  assert.equal(state.level, 'provinces');
  render(state, 120, 42, true);
  assert.deepEqual(state.hit.box, countryBox);
  assert.equal(handleMapClick(state, 0, 0), false);
});

test('raster: relleno, agujeros y coordenadas fuera de la ventana', () => {
  const rings = ringsFromPath('M0 0L10 0L10 10L0 10ZM3 3L7 3L7 7L3 7Z');
  const grid = rasterize([{ id: 9, rings }], [0, 0, 10, 10], 10, 10);
  assert.equal(grid[0], 9);
  assert.equal(grid[5 * 10 + 5], -1);
  assert.equal(grid[9 * 10 + 9], 9);
  assert.equal(rasterize([{ id: 9, rings }], [20, 20, 10, 10], 10, 10).every(x => x === -1), true);
  assert.equal(rasterize([{ id: 9, rings }], [20, 0, 10, 10], 10, 10).every(x => x === -1), true);
  assert.equal(rasterize([{ id: 9, rings }], [-20, 0, 10, 10], 10, 10).every(x => x === -1), true);
  assert.throws(() => ringsFromPath('M0 0C1 1 2 2 3 3Z'), /no admitidos/);
});

test('Jujuy 1920: mantiene relleno de reserva y no aparece en más ajustadas', () => {
  const a = get('1920'), m = modeOf(a, 'gan');
  const ids = a.data.territories.flatMap((t, i) => t.p === 'Jujuy' ? [i] : []);
  assert.ok(ids.length > 0);
  assert.ok(ids.some(i => m.units[i].lines?.length));
  for (const id of ids) {
    assert.ok(m.units[id].fill, 'No se debe deducir ganador de las cifras');
    assert.equal(fillFor(a, m, id), m.units[id].fill);
  }
  assert.ok(closest(a).every(r => !ids.includes(r.id)));
  for (const id of ids) assert.equal(provinceFill(a, m, id), m.prov.Jujuy.fill);
});

test('1999 diputados: provincias sólidas no inventan ficha departamental', () => {
  const a = get('1999dip'), m = modeOf(a, 'gan');
  const id = a.data.territories.findIndex(t => t.p === 'San Luis');
  assert.ok(a.data.solid.includes('San Luis'));
  assert.equal(recordFor(a, m, id), m.prov['San Luis']);
  const s = makeState(a, { selected: id });
  const output = render(s, 120, 42, false);
  assert.ok(!output.includes('\x1b'));
  assert.ok(closest(a).every(r => a.data.territories[r.id].p !== 'San Luis'));
});

test('2009 por radio: conserva las exclusiones de Morón', () => {
  const a = get('amba_2009dip'), m = modeOf(a, 'gan');
  const excluded = m.units.filter(r => r.note && /NE resulta primero en esta estimación/i.test(r.note) && r.fill);
  assert.equal(excluded.length, 321);
  const id = m.units.indexOf(excluded[0]);
  assert.equal(fillFor(a, m, id), excluded[0].fill);
  assert.ok(!closest(a).some(r => r.id === id));
  assert.match(m.note, /estimaci|estimad/i);
});

test('más ajustadas: orden, diferencia y exclusión de blancos/nulos', () => {
  const ranked = closest(bal);
  assert.ok(ranked.length > 500);
  assert.ok(ranked.every((r, i) => i === 0 || r.gap >= ranked[i - 1].gap));
  for (const r of ranked) {
    assert.equal(r.gap, r.lines[0][2] - r.lines[1][2]);
    assert.ok(r.lines.every(l => l[0] === 'LLA' || l[0] === 'UP'));
  }
});

test('teclado: filtra sin tildes, abre ficha y cambia modo sin alterar votos', () => {
  const state = makeState(bal, { entries, mode: undefined });
  assert.equal(state.mode.id, 'gan');
  handleKey(state, '/', { name: '/' });
  handleKey(state, 'La Matanza', {});
  handleKey(state, '\r', { name: 'return' });
  assert.equal(bal.data.territories[state.selected].n, 'La Matanza', 'Un solo Enter abre la ficha');
  render(state, 100, 32, false);
  assert.equal(bal.data.territories[state.selected].n, 'La Matanza');
  const lines = JSON.stringify(state.mode.units[state.selected].lines);
  handleKey(state, 'm', {});
  assert.equal(state.mode.id, 'lla');
  assert.equal(JSON.stringify(state.mode.units[state.selected].lines), lines);
  handleKey(state, 'r', {});
  assert.equal(state.selected, null);
  handleKey(state, 'q', {});
  assert.equal(handleKey(state, 'q', {}), 'quit');
});

test('selector: flechas mientras se filtra, Enter único y escritura antes del redibujado', () => {
  const state = makeState(bal, { entries });
  handleKey(state, 'a', {});
  const original = state.cursor;
  handleKey(state, '', { name: 'down' });
  assert.equal(state.cursor, original + 1);
  assert.equal(state.editing, true);
  assert.equal(handleKey(state, '\r', { name: 'return' }).path, entries[original + 1].path);
  handleKey(state, 'a', {});
  handleKey(state, '2023 balotaje', {});
  const entry = handleKey(state, '\r', { name: 'return' });
  assert.ok(entry.title.includes('balotaje'));
  assert.ok(entry.year === '2023');
});

test('selector: clic abre la fila visible después de desplazarse', () => {
  const state = makeState(bal, { entries });
  handleKey(state, 'a', {});
  handleKey(state, '', { name: 'end' });
  render(state, 100, 30, true);
  const hit = state.panelHit;
  assert.ok(hit.offset > 0);
  const target = handleClick(state, hit.x + 2, hit.y + 1);
  assert.equal(target.path, state.items[hit.offset + 1].entry.path);
});

test('AMBA y Capital: botones directos acercan sus ventanas y permiten elegir unidades', () => {
  const state = makeState(bal, { entries });
  render(state, 120, 42, true);
  const country = state.hit.box;
  const button = state.buttons.find(b => b.key === 'b');
  handleClick(state, button.x, button.y);
  render(state, 120, 42, true);
  assert.equal(state.atlas.data.insets[state.inset].id, 'gba');
  assert.ok(state.hit.box[2] < country[2] / 5);
  assert.ok(handleMapClick(state, ...mapCoordinate(state, id => /capital|ciudad de buenos aires/i.test(state.atlas.data.territories[id].p))));
  assert.ok(state.selected != null);
  const inset = state.inset;
  handleKey(state, '', { name: 'escape' });
  assert.equal(state.inset, inset);
  handleKey(state, 'd', {});
  render(state, 120, 42, true);
  assert.equal(state.atlas.data.insets[state.inset].id, 'caba');
  handleKey(state, 'a', {});
  render(state, 120, 42, true);
  const metroButton = state.buttons.find(b => b.key === 'b');
  handleClick(state, metroButton.x, metroButton.y);
  assert.equal(state.view, 'map');
  assert.equal(state.editing, false);
  assert.equal(state.atlas.data.insets[state.inset].id, 'gba');
});

test('redibujado: mover selección sólo actualiza el panel, sin limpiar ni tocar el mapa', () => {
  const state = makeState(bal, { entries });
  handleKey(state, 'a', {});
  const before = render(state, 120, 42, true).split('\n');
  handleKey(state, '', { name: 'down' });
  const after = render(state, 120, 42, true).split('\n');
  const patch = framePatch(before, after, 120, 42);
  assert.ok(patch.length > 0);
  assert.ok(!patch.includes('\x1b[2J'));
  assert.ok([...patch.matchAll(/\x1b\[(\d+);(\d+)H/g)].every(m => Number(m[2]) >= state.panelHit.x));
  assert.ok(patch.length < before.join('\n').length / 10);
  assert.equal(framePatch(after, after, 120, 42), '');
  assert.deepEqual(cells('\x1b[38;2;1;2;3mA\x1b[0mB'), [{ ch: 'A', fg: '38;2;1;2;3', bg: '49' }, { ch: 'B', fg: '39', bg: '49' }]);
});

test('proporciones: la relación física del dibujo conserva la del SVG para distintas fuentes', () => {
  for (const cellAspect of [1.5, 1.8, 2, 2.2, 2.6]) {
    const state = makeState(bal, { cellAspect });
    render(state, 140, 55, true);
    const expected = state.hit.box[2] / state.hit.box[3];
    const physical = state.hit.width / state.hit.height * 2 / cellAspect;
    assert.ok(Math.abs(physical / expected - 1) < .07, `Celda ${cellAspect}: ${physical} vs ${expected}`);
  }
  assert.equal(parseArgs(['--aspect', '1.8']).aspect, '1.8');
  assert.throws(() => parseArgs(['--aspect', '0']), /alto\/ancho/);
});

test('mapa: tamaño, selección y recuadros; no muta el atlas', () => {
  const state = makeState(bal, { entries });
  const before = JSON.stringify(bal.data.modes[0]);
  const text = render(state, 110, 38, false);
  assert.equal(text.split('\n').length, 37);
  assert.ok(state.grid.some(x => x >= 0));
  assert.ok(state.hit.width < 110);
  assert.match(render(state, 110, 38, true), /\x1b\[38;2;/);
  handleKey(state, 'i', {});
  render(state, 110, 38, false);
  assert.equal(state.inset, 0);
  assert.equal(JSON.stringify(bal.data.modes[0]), before);
});

test('CLI redirigida: salida sin ANSI, JSON exacto, validación de argumentos', () => {
  const script = resolve(ROOT, 'herramientas/atlas_terminal/atlas.mjs');
  const run = args => spawnSync(process.execPath, [script, ...args], { encoding: 'utf8', cwd: ROOT });
  const printed = run(['2023bal', '--print', '--width', '100', '--height', '30']);
  assert.equal(printed.status, 0, printed.stderr);
  assert.ok(!printed.stdout.includes('\x1b'));
  assert.match(printed.stdout, /14.554.560/);
  const json = run(['2023bal', '--search', 'La Matanza', '--json']);
  assert.equal(json.status, 0, json.stderr);
  const data = JSON.parse(json.stdout);
  assert.equal(data.units.length, 1);
  assert.equal(data.units[0].territory.n, 'La Matanza');
  assert.equal(data.national.cands[0].votes, 14554560);
  assert.ok(!JSON.stringify(data).includes('data:image'));
  assert.throws(() => parseArgs(['--mode']), /Falta/);
  assert.throws(() => parseArgs(['--width', 'NaN']), /entero/);
  assert.throws(() => modeOf(bal, 'inventado'), /Modo desconocido/);
  const bad = run(['2023bal', '--mode', 'inventado']);
  assert.equal(bad.status, 1);
});

test('Windows: compila el adaptador de clics de consola clásica', { skip: process.platform !== 'win32' }, () => {
  const path = resolve(ROOT, 'herramientas/atlas_terminal/ConsoleMouse.cs').replaceAll("'", "''");
  const code = `$ErrorActionPreference='Stop'; Add-Type -Path '${path}'; 'compiled'`;
  const result = spawnSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-EncodedCommand', Buffer.from(code, 'utf16le').toString('base64')], { encoding: 'utf8', windowsHide: true });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /compiled/);
});
