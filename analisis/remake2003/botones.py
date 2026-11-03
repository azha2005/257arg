"""Pestañas de ancho medido, separadas, sólo para los ocho remakes."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'mapas/mapa2003alt'
DRAW_TILES='''function drawTiles(){
  const g=$("#tiles");g.replaceChildren();
  const list=tilesNow(),gap=8,right=1490;
  const rows=list.map(([m,t])=>{
    const gg=el("g",{class:"tile"+(m===MODE?" on":""),"data-mode":m},g);
    const rect=el("rect",{x:0,y:28,width:62,height:62},gg);
    const text=el("text",{x:0,y:64,style:"font-size:15px"},gg,t);
    const width=Math.max(62,Math.ceil(text.getComputedTextLength())+20);
    gg.addEventListener("click",()=>setMode(m));
    return {rect,text,width};
  });
  let x=right-rows.reduce((sum,r)=>sum+r.width,0)-gap*Math.max(0,rows.length-1);
  rows.forEach(r=>{
    r.rect.setAttribute("x",x);r.rect.setAttribute("width",r.width);
    r.text.setAttribute("x",x+r.width/2);x+=r.width+gap;
  });
}
'''

def patch_tiles(html):
    a=html.index('function drawTiles(){');b=html.index('\n}\n',a)+3
    return html[:a]+DRAW_TILES+html[b:]

def main():
    paths=list(DEST.glob('atlas_2003alt_*.html'))
    for p in paths:p.write_text(patch_tiles(p.read_text('utf8')),'utf8')
    print('Botones separados y de ancho medido:',len(paths),'atlas.')

if __name__=='__main__':main()
