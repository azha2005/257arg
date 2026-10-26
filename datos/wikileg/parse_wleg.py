import re, sys
def clean(s):
    s=re.sub(r'<ref.*?</ref>|<ref[^>]*/>','',s,flags=re.S)
    s=re.sub(r'\{\{[^{}]*\}\}','',s)
    s=re.sub(r'\[\[([^\]|]*)\|([^\]]*)\]\]',r'\2',s); s=re.sub(r'\[\[([^\]]*)\]\]',r'\1',s)
    s=re.sub(r"'''?",'',s); s=re.sub(r'<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',s).strip()
def table_after(text, heading):
    i=text.index(heading); j=text.index('{|',i); k=text.index('\n|}',j)
    return text[j:k]
def rows(tbl):
    out=[]
    for blk in tbl.split('\n|-'):
        cells=[c.strip() for c in re.split(r'\n\||\n!',blk)[1:]]
        if not cells: continue
        col=None; m=re.search(r'Color político\|([^}|]+)',blk,re.I)
        if m: col=m.group(1).strip()
        else:
            m=re.search(r'#([0-9A-Fa-f]{6})',blk); col=('#'+m.group(1)) if m else None
        # nombre y votos: primera celda con un numero de votos >= 1000 despues de una celda con texto
        for n,c in enumerate(cells):
            value=re.sub(r'^[^|]*\|\s*', '', clean(c))
            v=re.fullmatch(r'\s*(\d{1,3}(?:[.,]\d{3})+)\s*',value)
            if v and n>0:
                votos=int(re.sub(r'[.,]','',v.group(1)))
                name_cell=cells[n-1]
                link=re.search(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]',name_cell)
                out.append(dict(nombre=clean(name_cell), link=link.group(1) if link else '', color=col, votos=votos))
                break
    return out
if __name__=='__main__':
    y=sys.argv[1]; head=sys.argv[2] if len(sys.argv)>2 else '=== Diputados ==='
    t=open(f'datos/wikileg/wleg{y}.txt',encoding='utf8').read()
    tb=table_after(t,head)
    r=rows(tb); print(y,head,len(r),'filas, suma',sum(x['votos'] for x in r))
    for x in r[:60]: print(' ',x['votos'],'|',x['nombre'][:45],'|',x['link'][:30],'|',x['color'])
