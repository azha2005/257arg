"""Créditos de los autores de las ucronías, separados de la estimación local."""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
AUTHORS={
 'mapas/mapa2027/atlas_2027.html':('@boluanfanzheng',None,'dataset_2027.json'),
 'mapas/mapa2027kic/atlas_2027kic.html':('@boluanfanzheng',None,'dataset_2027kic.json'),
 'mapas/mapa1985hip/atlas_1985hip.html':('@fedepdice_',None,'dataset_1985hip.json'),
 'mapas/mapa1916fic/atlas_1916_alt.html':('@etiamintenebris',None,'dataset_1916fic.json'),
}

def aplicar(path):
    path=Path(path).resolve();relative=path.relative_to(ROOT).as_posix()
    if relative.startswith('mapas/mapa2003alt/atlas_2003alt_'):
        author,url='u/Alarmed_Rope5383','https://www.reddit.com/user/Alarmed_Rope5383/'
        dataset=path.name.replace('atlas_','dataset_').replace('.html','.json')
    else:author,url,dataset=AUTHORS[relative]
    text=path.read_bytes().decode('utf8');newline='\r\n' if '\r\n' in text else '\n'
    a=text.index('const DATA=');b=text.index('const START_MODE=',a)
    ds=json.JSONDecoder().raw_decode(text[a+len('const DATA='):].lstrip())[0]
    credit=f'Escenario y mapas originales: {author}. Remake y estimación territorial: Atlas electorales argentinos.'
    ds['credits']=dict(original_author=author,original_profile=url,remake='Atlas electorales argentinos',scope='Escenario original; no atribuye al autor las cifras locales estimadas del remake.')
    for mode in ds['modes']:
        if credit not in mode.get('note',''):mode['note']=mode.get('note','').rstrip()+' '+credit
    payload=json.dumps(ds,ensure_ascii=False,separators=(',',':'))
    text=text[:a]+'const DATA='+payload+';'+newline+text[b:]
    # Crédito legible y, cuando se proporcionó perfil, enlazado desde la barra.
    text=re.sub(r'<div class="grp" id="credito-escenario">.*?</div>\s*','',text,flags=re.S)
    name=f'<a href="{url}" target="_blank" rel="noopener" style="color:inherit">{author}</a>' if url else f'<span>{author}</span>'
    markup=f'<div class="grp" id="credito-escenario"><span>Escenario original:</span> {name}</div>'+newline
    assert text.count('<div id="barnote"></div>')==1,path
    text=text.replace('<div id="barnote"></div>',markup+'<div id="barnote"></div>',1)
    path.write_bytes(text.encode('utf8'))
    dp=path.parent/dataset;old=dp.read_bytes().decode('utf8') if dp.exists() else ''
    compact=old.count('\n')<=1
    dp.write_text(json.dumps(ds,ensure_ascii=False,separators=(',',':')) if compact else json.dumps(ds,ensure_ascii=False,indent=2),'utf8')
    return author

if __name__=='__main__':
    for relative in AUTHORS:print(relative,aplicar(ROOT/relative))
    for p in (ROOT/'mapas/mapa2003alt').glob('atlas_2003alt_*.html'):print(p.name,aplicar(p))
