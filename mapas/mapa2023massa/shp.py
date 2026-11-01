"""Lector minimo de .shp/.dbf (solo poligonos) sin dependencias."""
import struct

def read_dbf(path):
    f = open(path, 'rb').read()
    n = struct.unpack('<I', f[4:8])[0]; hl = struct.unpack('<H', f[8:10])[0]; rl = struct.unpack('<H', f[10:12])[0]
    fields = []; o = 32
    while f[o] != 0x0D:
        fields.append((f[o:o+11].split(b'\0')[0].decode(), f[o+16])); o += 32
    rows = []
    for i in range(n):
        r = f[hl+i*rl+1: hl+(i+1)*rl]; p = 0; d = {}
        for nm, l in fields:
            d[nm] = r[p:p+l].decode('utf8', 'replace').strip(); p += l
        rows.append(d)
    return rows

def read_shp(path):
    f = open(path, 'rb').read()
    o = 100; out = []
    while o < len(f):
        _, clen = struct.unpack('>ii', f[o:o+8]); o += 8
        rec = f[o:o+clen*2]; o += clen*2
        st = struct.unpack('<i', rec[:4])[0]
        if st == 0: out.append([]); continue
        np_, nv = struct.unpack('<ii', rec[36:44])
        parts = list(struct.unpack('<%di' % np_, rec[44:44+4*np_]))
        pts = struct.unpack('<%dd' % (2*nv), rec[44+4*np_: 44+4*np_+16*nv])
        pts = [(pts[2*i], pts[2*i+1]) for i in range(nv)]
        parts.append(nv)
        out.append([pts[parts[i]:parts[i+1]] for i in range(np_)])
    return out
