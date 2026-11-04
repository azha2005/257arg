"""Informe reproducible desde los CSV guardados; no selecciona parametros."""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
P=HERE.parent
SC={'azar':'30 al azar','twitter':'30 tipo Twitter','twitter_parcial':'30 Twitter, 10 parciales'}


def main():
    before=pd.read_csv(HERE/'fotos_antes.csv');after=pd.read_csv(HERE/'fotos_despues.csv')
    assert (after.actas==30).all()
    assert before.actas.between(1,30).all()
    for d in [before,after]:
        d['abs_margen']=d.error_margen.abs()
        d['ancho']=d.hi-d.lo
    keys=['destino','esquema','rep']
    paired=before.merge(after,on=keys,suffixes=('_antes','_despues'),validate='one_to_one')
    assert len(paired)==1000
    stats=[]
    rng=np.random.default_rng(1828)
    for (dest,scheme),g in paired.groupby(['destino','esquema'],sort=False):
        diff=g.abs_margen_despues-g.abs_margen_antes
        sim=rng.choice(diff.to_numpy(),size=(3000,len(diff))).mean(1)
        lo,hi=np.quantile(sim,[.025,.975])
        stats.append(dict(destino=dest,esquema=scheme,n=len(g),
                          mae_margen_antes=g.abs_margen_antes.mean(),mae_margen_despues=g.abs_margen_despues.mean(),
                          mae_fuerzas_antes=g.mae_fuerzas_antes.mean(),mae_fuerzas_despues=g.mae_fuerzas_despues.mean(),
                          cobertura_antes=g.cubre_antes.mean(),cobertura_despues=g.cubre_despues.mean(),
                          ancho_antes=g.ancho_antes.mean(),ancho_despues=g.ancho_despues.mean(),
                          diferencia=diff.mean(),ic_mc_lo=lo,ic_mc_hi=hi))
    st=pd.DataFrame(stats);st.to_csv(HERE/'resumen_fotos.csv',index=False)
    L=['# Correcciones implementadas y medición de la proyección argentina','',
       '28 de octubre de 2026. Código anterior conservado en `baseline/`. No se cambiaron las transcripciones ni se incorporaron votos inventados.',
       '', '## Resultado principal','',
       'La corrección mejora modestamente los porcentajes nacionales y evita errores de identidad, datos ausentes y probabilidades. No se encontró una mejora uniforme en bancas. Se conservan Goodman λ=0,1 y factor 1,4 para fotos; no se retocaron para acertar las 27 actas reales.',
       '', '## Qué se corrigió','',
       '- El backtest mantiene todo voto disponible de destino, con respaldo histórico por circuito, sección o distrito. Las filas sin resultados finales se distinguen de abstenciones; no se imputa su voto.',
       '- El repesado AMBA/resto se calcula sobre las actas que informan cada fuerza y se repite en cada remuestra.',
       '- Identidad electoral independiente del nombre de la foto; se colapsan copias iguales y se rechazan versiones contradictorias.',
       '- Catálogo de fuerzas separado de las fotos; cero observado, desconocido y lista no presentada son estados distintos. Sin soporte, bandas y probabilidades quedan no estimables.',
       '- Primer puesto se compara contra todas las fuerzas, no solo contra el segundo de la estimación puntual.',
       '- Porcentajes nacionales y bancas salen de los mismos votos distritales y remuestras. Las actas parciales no reducen el prior de una fuerza no informada. La actualización provincial remuestrea las actas y su covarianza con el modelo.',
       '- Se usa padrón de destino y se prohíben votos a listas ausentes de cada distrito. Las tablas agregadas OTRAS no se interpretan como fotos con detalle de listas provinciales.',
       '- La aguja masiva usa D sin benchmarking y remuestrea el estimador completo, manteniendo fijos los votos ya conocidos. El prior del ICG usa solo años anteriores por defecto y sigue desactivado en la proyección de fotos.',
       '', '## Diseño de la medición','',
       '1.000 colecciones de exactamente 30 mesas por versión: 100 por combinación de elección destino y esquema. Destinos: balotajes 2015 y 2023, general 2023 y diputados 2025. Para las generales se promedian dos orígenes, como el programa operativo. Son cuatro elecciones destino, no 1.000 elecciones independientes.',
       '',
       'Azar: 30 mesas uniformes. Tipo Twitter: 20 del AMBA y 10 del resto, con racimos AMBA de hasta 10+3+3 mesas y completando siempre a 30 únicas. Twitter parcial: mismo diseño, ocultando a terceros en las primeras diez actas; se mantienen los dos principales del destino como escenario sintético. No reproduce todos los mecanismos reales de publicación de fotos.',
       '',
       'Ambas versiones reciben las mismas 30 mesas y se comparan contra todo el provisorio disponible. La anterior descarta actas sin cruce histórico y retiene entre 28 y 30; la corregida conserva las 30 en las 1.000 corridas. La columna actas de los CSV cuenta las retenidas, no las entregadas. La nueva usa el marco de electores de destino y respaldo de origen; la anterior mantiene su comportamiento original. Los electores por mesa de las fotos no se entregan al modelo: los estima como en operación. Cada corrida usa 200 remuestras de circuitos. El factor de banda 1,4 estaba fijado antes de estas pruebas. Las semillas son nuevas, pero las elecciones ya se habían usado en el desarrollo: esto es evaluación retrospectiva emparejada, no validación prospectiva.',
       '', '## Error del margen y cobertura','',
       'Errores en puntos porcentuales. Cobertura de banda nominal 95 %, medida para el margen entre los dos primeros reales. Con 100 colecciones, diferencias de pocos puntos de cobertura tienen incertidumbre de Monte Carlo apreciable.',
       '', '| Destino | Muestra | Error antes | Error después | Cobertura antes | Cobertura después |',
       '|---|---|---:|---:|---:|---:|']
    for r in stats:
        L.append('| %s | %s | %.3f | %.3f | %.0f %% | %.0f %% |'%(r['destino'],SC[r['esquema']],r['mae_margen_antes'],r['mae_margen_despues'],100*r['cobertura_antes'],100*r['cobertura_despues']))
    L+=['','La ganancia del margen no es uniforme: en general 2023 sube unas centésimas y en otros pares baja. `resumen_fotos.csv` incluye diferencias emparejadas e intervalos Monte Carlo; estos cuantifican las colecciones simuladas y no la incertidumbre sobre futuras elecciones.',
        '', '## Error por fuerza','', '| Destino | Muestra | Media antes | Media después |','|---|---|---:|---:|']
    for r in stats:L.append('| %s | %s | %.3f | %.3f |'%(r['destino'],SC[r['esquema']],r['mae_fuerzas_antes'],r['mae_fuerzas_despues']))
    L+=['','Con fotos parciales, la reducción del error medio por fuerza es 8,5 % en 2023 y 5,3 % en 2025. Esto no implica una reducción equivalente del margen.',
        '', '## Bancas: 50 colecciones por esquema','',
        'Se midieron 150 colecciones por versión, 100 remuestras cada una, con las primeras 50 muestras de cada esquema de 2025. La referencia real son las bancas calculadas a partir de listas y padrón locales: LLA 64, FP 47, PU 8, FIT 3, otras 5. Ambos modelos conservan el prior provincial y el supuesto Zipf; la nueva versión corrige su aplicación y hace coherente el nacional.',
        '', '| Muestra | Fuerza | Error absoluto antes | Error absoluto después | Cobertura 90 % antes | Después |','|---|---|---:|---:|---:|---:|']
    banks=[]
    for v in ['antes','despues']:
        b=pd.read_csv(HERE/('bancas_'+v+'_escanos.csv'));b['abs_error']=b.error.abs()
        banks.append(b.groupby(['esquema','fuerza'])[['abs_error','cubre','error']].mean().add_suffix('_'+v))
    bs=banks[0].join(banks[1]);bs.to_csv(HERE/'resumen_bancas.csv')
    for (scheme,f),r in bs.iterrows():
        L.append('| %s | %s | %.2f | %.2f | %.0f %% | %.0f %% |'%(SC[scheme],f,r.abs_error_antes,r.abs_error_despues,100*r.cubre_antes,100*r.cubre_despues))
    L+=['','No hubo mejora uniforme: persiste la subestimación de LLA y la sobreestimación de fuerzas menores en parte de las simulaciones. No se ajustó el perfil Zipf ni la retención de gobernadores con estos errores de 2025. La corrección del procedimiento sigue siendo necesaria, aunque empeore alguna métrica: evita aparentes aciertos producidos por errores que se compensan.',
        '', '## Las actas reales de Twitter','',
        'Son 27 mesas únicas en 16 circuitos, 20 del AMBA y 11 actas incompletas. Se usaron las transcripciones originales, sin seleccionar una submuestra favorable. Punto nacional: 2.000 remuestras; Congreso: 300 de las mismas remuestras.',
        '', '| Fuerza | Antes, sin corrección provincial nacional | Corregido, sin prior provincial | Corregido, coherente con Congreso | Real |',
        '|---|---:|---:|---:|---:|']
    rb=json.loads((HERE/'twitter_real_antes.json').read_text(encoding='utf-8'))
    ra=json.loads((HERE/'twitter_real_despues.json').read_text(encoding='utf-8'))
    for f in ['LLA','FP','PU','FIT','OTRAS']:
        L.append('| %s | %.2f | %.2f | %.2f | %.2f |'%(f,rb['sin_prior_provincial']['punto'][f],ra['sin_prior_provincial']['punto'][f],ra['con_prior_provincial']['punto'][f],ra['real'][f]))
    L+=['', 'Margen LLA−FP: antes **%+.3f**, corregido sin prior provincial **%+.3f**, conjunto votos+bancas **%+.3f**; real **%+.3f**.'%(rb['sin_prior_provincial']['margen'],ra['sin_prior_provincial']['margen'],ra['con_prior_provincial']['margen'],ra['real_margen']),
        '', 'Bancas corregidas: **LLA 62, FP 49, PU 8, FIT 3, otras 5**. El punto no cambió respecto de la versión previa con gobernadores: dos bancas transferidas de LLA a FP respecto de la referencia real. Las bandas ahora provienen de las mismas remuestras que los porcentajes nacionales.',
        '', 'El buen margen de estas 27 mesas no vuelve exacto el detalle: OTRAS sigue subestimado aproximadamente 2,6 puntos en el modelo con Congreso.',
        '', '## Escrutinio masivo y cobertura fuera de la calibración','']
    d=pd.read_csv(HERE/'escrutinio_completo.csv');d['abs_error']=d.error.abs()
    pivot=d.groupby(['par','metodo']).abs_error.mean().unstack()
    L+=['Seis repeticiones por tipo de llegada (cinco tipos), cinco cortes (0,2 %, 1 %, 5 %, 25 %, 50 %) y tres métodos: 1.350 evaluaciones. Todos incluyen los 24 distritos y el 100 % de votos disponibles en los archivos de destino. No significa 100 % de votos definitivos: las mesas sin resultados en el provisorio siguen siendo desconocidas.',
        '', '| Par | D con benchmarking | D sin ajuste | E sin ajuste |','|---|---:|---:|---:|']
    for par,r in pivot.iterrows():L.append('| %s | %.3f | %.3f | %.3f |'%(par,r['D'],r.D_sin_ajuste,r.E_sin_ajuste))
    L+=['','Se implementó D sin ajuste como base de la aguja. E queda como variante experimental: su ventaja todavía debe contrastarse en otros destinos. El benchmarking podía introducir votos negativos después del recorte; en esta prueba D llegó a %.2f votos en una celda. D y E sin ajuste conservaron no negatividad.'%d[d.metodo=='D'].minimo_votos.min(),
        '', 'Para el error sistemático entre años se añadió un piso de desviación `1,8 × (1−fracción)`, calibrado exclusivamente con 2019→2023 donde la fórmula anterior quedaba corta. Se evaluó sin retocarlo con 2023→2025: 3 trayectorias por cada uno de 5 órdenes, 4 cortes, 60 remuestras por corte. Es una prueba pequeña y los cortes de una trayectoria son dependientes.',
        '', '| Orden | Cobertura LLA | FP | PU | FIT | OTRAS |','|---|---:|---:|---:|---:|---:|']
    cov=pd.read_csv(HERE/'aguja_cobertura_2025.csv').groupby(['esquema','fuerza']).cubre.mean().unstack()
    for scheme,r in cov.iterrows():L.append('| %s | %s |'%(scheme,' | '.join('%.1f %%'%(100*r[f]) for f in ['LLA','FP','PU','FIT','OTRAS'])))
    L+=['','**Limitación abierta:** en el estrés donde entran primero las secciones favorables al ganador, la cobertura de LLA queda en 66,7 % y la de OTRAS en 41,7 %. No se presenta esta banda como calibrada al 95 % para cualquier selección. La página muestra bandas nominales y frecuencias de simulación con esta reserva. No se amplió a posteriori usando 2025 para aparentar que pasó la prueba.',
        '', '## Pruebas y reproducción','',
        '11 pruebas de regresión pasan: duplicados y conflictos, pesos por fuerza, catálogo y datos ausentes, probabilidad conjunta, prior provincial con actas parciales, respaldo histórico, identidad de votos/bancas, equivalencia numérica de la ruta optimizada y conservación de todos los votos observados.',
        '', '```powershell',
        'python -X utf8 proyeccion/validacion_20261028/medir.py --version antes --reps 100 --boot 200',
        'python -X utf8 proyeccion/validacion_20261028/medir.py --version despues --reps 100 --boot 200',
        'python -X utf8 proyeccion/validacion_20261028/medir.py --version antes --reps 50 --boot 100 --destinos 2025bl --bancas',
        'python -X utf8 proyeccion/validacion_20261028/medir.py --version despues --reps 50 --boot 100 --destinos 2025bl --bancas',
        'python -X utf8 proyeccion/validacion_20261028/escrutinio.py',
        'python -X utf8 proyeccion/validacion_20261028/cobertura_aguja.py',
        'python -X utf8 proyeccion/validacion_20261028/reales.py antes',
        'python -X utf8 proyeccion/validacion_20261028/reales.py despues',
        'python -W ignore::DeprecationWarning -W ignore::ResourceWarning -X utf8 proyeccion/test_correcciones.py',
        'python -X utf8 proyeccion/proyectar_fotos.py proyeccion/fotos25/actas.csv --origen 2023p,2021bl --real 2025bl --congreso 2025',
        'python -X utf8 proyeccion/aguja_fotos.py',
        'python -X utf8 proyeccion/validacion_20261028/informe.py','```','',
        'Para una elección futura: proporcionar `--marco` con distrito_id, seccion_id, circuito, e, más el catálogo de fuerzas y los antecesores revisados. Las fotos pueden incluir `electores`; si falta se estima desde el origen. Para Congreso son obligatorios el padrón y el catálogo de listas del año; no se reutiliza silenciosamente el padrón de una elección anterior.',
        '', '## Archivos','',
        '- `fotos_antes/despues.csv` y `_fuerzas.csv`: resultados por muestra y por fuerza.',
        '- `bancas_antes/despues_escanos.csv`: comparación de las bancas por muestra.',
        '- `resumen_fotos.csv`, `resumen_bancas.csv`: tablas agregadas.',
        '- `twitter_real_antes/despues.json`: las 27 actas reales.',
        '- `universos_completos.json`, `escrutinio_completo.csv`, `aguja_cobertura_2025.csv`: universo, modelos y prueba de bandas.',
        '- `baseline/`: copia previa de los modelos y de los informes/gráfico reales; los otros informes históricos fuera de esta carpeta conservan su fecha y método anterior.',
        '- `../fotos25/actas_proyeccion.md`, `../fotos25/actas_congreso.html`, `../img/aguja_fotos_2025.png`: salidas operativas actualizadas.',
        '', '![Comparación de 30 mesas](comparacion_30_mesas.png)', '']
    (HERE/'RESULTADOS.md').write_text('\n'.join(L),encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,axs=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    subset=st[st.destino=='2025bl'].set_index('esquema').loc[list(SC)]
    y=np.arange(3);h=.32
    for ax,metric,title in [(axs[0],'mae_margen','Error absoluto del margen LLA−FP'),(axs[1],'mae_fuerzas','Error absoluto medio por fuerza')]:
        ax.barh(y-h/2,subset[metric+'_antes'],height=h,label='Anterior',color='#929ca8')
        ax.barh(y+h/2,subset[metric+'_despues'],height=h,label='Corregido',color='#166a88')
        for i,(_,r) in enumerate(subset.iterrows()):
            ax.text(r[metric+'_antes']+.025,i-h/2,'%.2f'%r[metric+'_antes'],va='center',fontsize=9)
            ax.text(r[metric+'_despues']+.025,i+h/2,'%.2f'%r[metric+'_despues'],va='center',fontsize=9)
        ax.set_yticks(y,[SC[k].replace('30 ','') for k in subset.index]);ax.invert_yaxis()
        ax.set_title(title,fontweight='bold',fontsize=11);ax.set_xlabel('Puntos porcentuales · menos es mejor')
        ax.set_xlim(0,subset[metric+'_antes'].max()*1.24)
        ax.spines[['top','right']].set_visible(False);ax.legend(loc='upper right',frameon=False)
    fig.suptitle('Diputados 2025 · 30 mesas por muestra',fontsize=15,fontweight='bold')
    fig.supxlabel('100 colecciones emparejadas por esquema. Twitter: 20 AMBA / 10 resto y racimos.\nLa mejora por fuerza no implica una mejora equivalente del margen.',fontsize=9)
    fig.savefig(HERE/'comparacion_30_mesas.png',dpi=160)
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [
        P/n for n in ['enlace.py','backtest.py','aguja.py','fotos_motor.py','fotos_modelo.py','proyectar_fotos.py',
                      'congreso.py','congreso_motor.py','aguja_fotos.py','aguja_dibujo.py',
                      'congreso_sim.py','icg/icg_fotos.py','test_correcciones.py']]}
    (HERE/'codigo_final_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(st.round(3).to_string(index=False))


if __name__=='__main__':main()
