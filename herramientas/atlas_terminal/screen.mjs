// Actualizaciones por celdas: la lista puede cambiar sin volver a pintar el mapa.
const CSI = '\x1b[';
const blank = { ch: ' ', fg: '39', bg: '49' };

export function cells(line = '') {
  const out = [];
  let fg = '39', bg = '49';
  for (const token of line.matchAll(/\x1b\[([\d;]*)m|([^\x1b])/gu)) {
    if (token[1] != null) {
      const codes = token[1].split(';').map(Number);
      for (let i = 0; i < codes.length; i++) {
        const code = codes[i];
        if (code === 0) { fg = '39'; bg = '49'; }
        else if (code === 39) fg = '39';
        else if (code === 49) bg = '49';
        else if ((code === 38 || code === 48) && codes[i + 1] === 2 && i + 4 < codes.length) {
          const value = codes.slice(i, i + 5).join(';'); i += 4;
          if (code === 38) fg = value; else bg = value;
        }
      }
    } else out.push({ ch: token[2], fg, bg });
  }
  return out;
}
const same = (a, b) => a.ch === b.ch && a.fg === b.fg && a.bg === b.bg;

export function framePatch(previous, next, width, height) {
  let patch = '';
  for (let row = 0; row < height; row++) {
    if (previous[row] === next[row]) continue;
    const before = cells(previous[row]), after = cells(next[row]);
    let col = 0;
    while (col < width) {
      if (same(before[col] || blank, after[col] || blank)) { col++; continue; }
      patch += `${CSI}${row + 1};${col + 1}H${CSI}0m`;
      let fg = '39', bg = '49';
      do {
        const cell = after[col] || blank;
        if (cell.fg !== fg) { patch += `${CSI}${cell.fg}m`; fg = cell.fg; }
        if (cell.bg !== bg) { patch += `${CSI}${cell.bg}m`; bg = cell.bg; }
        patch += cell.ch; col++;
      } while (col < width && !same(before[col] || blank, after[col] || blank));
    }
  }
  return patch ? patch + `${CSI}0m` : '';
}
