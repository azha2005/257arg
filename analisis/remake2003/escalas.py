"""Paletas y cortes exclusivos de los ocho remakes. No recalcula votos."""
from pathlib import Path
import colorsys,copy,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'mapas/mapa2003alt'
PALETTES=Path(__file__).resolve().parent/'paletas_originales.json'

def color_ramp(col):
    rgb=[int(col[i:i+2],16)/255 for i in (1,3,5)]
    hue,_,sat=colorsys.rgb_to_hls(*rgb)
    # Respaldo para fuerzas sin rellenos legibles: tonos con cuerpo, sin pastel.
    colors=[]
    for light in (.74,.64,.54,.44,.34,.24,.14):
        # Amarillos hacia ámbar al oscurecer, como la familia del proyecto.
        h=hue
        if 38<hue*360<68 and sat>.5:h-=(max(0,.64-light)/.48)*20/360
        values=colorsys.hls_to_rgb(h%1,light,sat)
        colors.append('#'+''.join(f'{round(x*255):02x}' for x in values))
    return colors

def apply_scales(ds,round_name):
    if round_name=='Primera vuelta':
        ds['bins']=[30,35,40,45,50,55]
        ds['bin_labels']=['<30%','30%','35%','40%','45%','50%','+55%']
    else:
        ds['bins']=[55,60,65,70,75,80]
        ds['bin_labels']=['<55%','55%','60%','65%','70%','75%','+80%']
    cand=ds['candidates']
    original=json.loads(PALETTES.read_text('utf8'))['scenarios'] if PALETTES.exists() else {}
    sid=ds['reconstruction']['national']['id']
    for code,c in cand.items():c['ramp']=original.get(sid,{}).get(code,{}).get('colors',color_ramp(c['base']))
    for mode in ds['modes']:
        records=mode['units']+list(mode.get('prov',{}).values())
        if mode['id']=='lectura':
            # La lectura categórica conserva exactamente su color plano anterior.
            for r in records:
                if r.get('w') and 'fill' not in r:
                    rgb=[int(cand[r['w']]['base'][i:i+2],16) for i in (1,3,5)]
                    r['fill']='#'+''.join(f'{round(x+(255-x)*.15):02x}' for x in rgb)
        elif mode['id']!='gan':
            code=next(c for c in cand if c.lower()==mode['id'])
            edges=[0,10,20,30,40,50,60]
            colors=cand[code]['ramp']
            mode['legend']['stops']=[[col,('+' if j==6 else '')+str(e)+'%'] for j,(col,e) in enumerate(zip(colors,edges))]
            for r in records:
                q=next((line[2] for line in r['lines'] if line[0]==code),None)
                if q is not None:r['fill']=colors[max(j for j,e in enumerate(edges) if q>=e)]

def patch_shader(html):
    old='const shade=(code,i)=>{const b=CAND[code].base;'
    new='const shade=(code,i)=>{const ramp=CAND[code].ramp;if(ramp&&ramp.length===7)return ramp[i];const b=CAND[code].base;'
    if new not in html:
        assert html.count(old)==1
        html=html.replace(old,new,1)
    return html

def fingerprint(ds):
    out=copy.deepcopy(ds)
    out.pop('bins',None);out.pop('bin_labels',None)
    for c in out['candidates'].values():c.pop('ramp',None)
    for m in out['modes']:
        for r in m['units']+list(m.get('prov',{}).values()):r.pop('fill',None)
        m.get('legend',{}).pop('stops',None)
    return hashlib.sha256(json.dumps(out,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def main():
    report=[]
    for p in sorted(DEST.glob('dataset_2003alt_*.json')):
        ds=json.loads(p.read_text('utf8'));before=fingerprint(ds)
        old_bins=ds.get('bins');old_labels=ds.get('bin_labels')
        apply_scales(ds,ds['reconstruction']['national']['round'])
        after=fingerprint(ds);assert before==after,p.name
        assert ds['bins']==old_bins and ds['bin_labels']==old_labels,p.name
        htmlp=p.with_name(p.name.replace('dataset_','atlas_').replace('.json','.html'))
        html=htmlp.read_text('utf8');a=html.index('const DATA=');b=html.index('const START_MODE=',a)
        html=html[:a]+'const DATA='+json.dumps(ds,ensure_ascii=False,separators=(',',':'))+';\n'+html[b:]
        htmlp.write_text(patch_shader(html),'utf8')
        p.write_text(json.dumps(ds,ensure_ascii=False,indent=2),'utf8')
        report.append(dict(atlas=p.stem,before_sha256=before,after_sha256=after,bins=ds['bins'],palettes={c:v['ramp'] for c,v in ds['candidates'].items()}))
    target=ROOT/'outputs/2003alt/control_escalas.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    print('Escalas actualizadas:',len(report),'atlas. Votos, porcentajes, ganadores, logos y colores base idénticos.')

if __name__=='__main__':main()
