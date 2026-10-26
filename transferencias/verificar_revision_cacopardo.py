"""Verifica los dos cruces recalculados y compara con el respaldo anterior."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright
import estimar as e
import sankey
from auditar import auditar

HERE=Path(__file__).resolve().parent
OUT=HERE/'revision_cacopardo_1967'
PAIRS=[('1954d','1965d'),('1958d','1962d')]

def main():
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport={'width':900,'height':930})
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        for a,b in PAIRS:
            pair=f'{a}_{b}';folder=HERE/pair
            ctl=json.loads((folder/'control.json').read_text(encoding='utf8'))
            before=json.loads((OUT/'anteriores'/pair/'control.json').read_text(encoding='utf8'))
            old=e.RATIO
            try:
                e.RATIO=tuple(ctl['filtro_razon_crecimiento'])
                A,B,*_,fresh=e.prepare(a,b)
            finally:e.RATIO=old
            assert fresh['usados']==ctl['usados']
            assert A.sum().astype(int).to_dict()==ctl['marginal_origen']
            assert B.sum().astype(int).to_dict()==ctl['marginal_destino']
            M=pd.read_csv(folder/'matriz_votos.csv',index_col=0)
            previous=pd.read_csv(OUT/'anteriores'/pair/'matriz_votos.csv',index_col=0)
            I=pd.read_csv(folder/'intervalos.csv')
            P=pd.read_csv(folder/'por_provincia.csv',dtype={'distrito':str})
            assert np.isfinite(M.values).all() and (M.values>=0).all()
            assert abs(M.values.sum()-B.values.sum())<=M.size
            assert len(I)==M.size and (I.p5<=I.p95).all()
            assert not P.duplicated(['distrito','origen','destino']).any()
            for district,g in P.groupby('distrito'):
                for dest,n in ctl['marginal_destino_provincia'][district].items():
                    if n==0:assert g[g.destino==dest].votos.sum()==0
            delta=(M.div(M.sum(1),axis=0)-previous.div(previous.sum(1),axis=0))*100
            delta.round(4).to_csv(folder/'cambio_vs_antes_cacopardo_pp.csv',encoding='utf-8-sig')
            sankey.main(a,b)
            page.goto((folder/f'sankey_{pair}.html').as_uri())
            options=page.locator('#v option').evaluate_all('xs=>xs.map(x=>({key:x.value,text:x.textContent}))')
            assert len(options)==P.distrito.nunique()+1
            page.screenshot(path=str(folder/f'sankey_{pair}.png'),full_page=True)
            for option in options:
                page.select_option('#v',option['key'])
                assert page.locator('.vista:visible').get_attribute('id')=='v-'+option['key']
                if option['key']=='nacional':continue
                group=P[P.distrito==option['key']]
                texts=page.locator('.vista:visible svg > text').all_text_contents()
                assert option['text'] in texts[0]
                for cat,n in group.groupby('destino').votos.sum().items():
                    if n>0:assert cat+': '+('%.1f'%(100*n/group.votos.sum())).replace('.',',')+' %' in texts
                if option['key']=='02':page.screenshot(path=str(folder/'PBA_revision_cacopardo.png'),full_page=True)
            audit=auditar(pair)
            item=dict(par=pair,antes=before['usados'],ahora=ctl['usados'],vistas=len(options),
                      ratio=ctl['filtro_razon_crecimiento'],max_cambio_pp_por_fila=delta.abs().max(1).round(3).to_dict(),
                      electores_origen_antes=before['electores_origen_usados'],electores_origen_ahora=ctl['electores_origen_usados'],
                      controles='OK',alertas=audit['imposibles'])
            results.append(item)
            lines=[f'# {pair}: revisión territorial con Cacopardo','',
                   f'[Abrir gráfico con selector](sankey_{pair}.html) | [PNG](sankey_{pair}.png)','',
                   f"Unidades: {before['usados']} antes, **{ctl['usados']} después**. La reducción proviene de agregar territorios, no de repartir votos.",
                   f"Filtro de crecimiento conservado: {ctl['filtro_razon_crecimiento']}. Penalización elegida de nuevo por validación cruzada: {ctl['lambda']}. Bootstrap: 200 remuestreos.",'',
                   ctl['correspondencias']['reserva'],'',
                   '[Cambios por celda frente al resultado anterior](cambio_vs_antes_cacopardo_pp.csv), [correspondencias](correspondencias.csv), [control](control.json), [fuentes y revisión completa](../revision_cacopardo_1967/LEEME.md).','',
                   'El respaldo completo anterior está en `../revision_cacopardo_1967/anteriores/`. Los intervalos no cubren toda la incertidumbre del modelo y de las fuentes.','',
                   'Filas no identificadas: '+(', '.join(r['origen'] for r in audit['filas'] if r['no_identificada']) or 'ninguna según el umbral de auditoría')+'.','']
            (folder/'RESUMEN.md').write_text('\n'.join(lines),encoding='utf8')
            print(pair,'OK',flush=True)
        assert not errors,errors
        browser.close()
    (OUT/'verificacion_recalculados.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
