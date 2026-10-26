from pathlib import Path
import json,re,collections
ROOT=Path(__file__).resolve().parents[1]
keys=[(f'mapa{y}dip',f'dataset_{y}dip.json',f'atlas_{y}_diputados.html',f'{y}dip') for y in [1983,1989,1995,1999]]+[('mapa2001bronca','dataset_2001bronca.json','atlas_2001bronca.html','2001bronca')]
for folder,df,hf,key in keys:
    d=json.loads((ROOT/folder/df).read_text(encoding='utf8'))
    h=(ROOT/folder/hf).read_text(encoding='utf8')
    embedded=json.loads(re.search(r'const DATA=(.*?);\n',h)[1]);assert embedded==d
    winners={r['w'] for r in d['modes'][0]['units'] if r.get('w')}
    assert winners=={c['code'] for c in d['modes'][0]['national']['cands']}
    for mode in d['modes']:
        assert len(mode['units'])==len(d['territories'])
        assert all(c in d['candidates'] for r in mode['units'] for c,v,p in r.get('lines',[]))
        assert len(mode['prov'])==24
        for out in ['png_transparentes','png_blanco']:
            png=ROOT/out/folder/(Path(hf).stem+'_'+mode['id']+'.png');assert png.exists()
            assert png.stat().st_mtime >= (ROOT/folder/hf).stat().st_mtime,('PNG desactualizado',png)
    package=ROOT/'commons'/key/'subir';n=len(d['modes'])
    assert len(list(package.glob('*.svg')))==n*2,(key,n)
    assert len(list(package.glob('*.png')))==n
    assert len(list(package.glob('*.txt')))==n*3
    assert all((f.with_name(f.name+'.txt')).exists() for f in package.iterdir() if f.suffix in ['.svg','.png'])
    print(key, 'OK',len(d['territories']),'polígonos',n,'modos',n*2,'SVG',n,'PNG')
a=json.loads((ROOT/'mapa1995dip/deseado_extrapolado.json').read_text(encoding='utf8'))['resultado']
assert a['m']['total']==28198 and sum(a['P'].values())==a['m']['positivos']==24534
d=json.loads((ROOT/'mapa2001bronca/dataset_2001bronca.json').read_text(encoding='utf8'))
nat=d['modes'][0]['national'];assert sum(s['v'] for s in nat['slices'])==18798991
assert next(c['votes'] for c in nat['cands'] if c['code']=='BRONCA')==4508883
assert all(not any(c in ('P_BLA','P_NUL') for c,v,p in r['lines']) for r in d['modes'][0]['units'])
print('Deseado: resta provincial exacta. Voto bronca: denominador y suma sin doble conteo OK.')
