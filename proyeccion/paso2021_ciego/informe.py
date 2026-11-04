"""Informe de la prueba reservada; no cambia parámetros ni predicciones."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
LABEL={'azar':'Azar','padron_distrito':'Padrón por distrito','racimos':'10 circuitos × 3 mesas','twitter':'Twitter: 20 AMBA / 10 resto','twitter_parcial':'Twitter con 10 parciales','geografico':'Circuitos pequeños','sesgo_historico':'Sesgo FDT del antecedente'}
MODELS=['congelado','temporal','swing','crudo','crudo_ponderado','solo_2019','sin_repesado','sin_regularizar']

def wilson(p,n):
 z=1.96;center=(p+z*z/(2*n))/(1+z*z/n);half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
 return center-half,center+half

def main():
 cfg=json.loads((HERE/'PARAMETROS_SELLADOS.json').read_text());truth=json.loads((HERE/'REAL_ABIERTO.json').read_text())
 d=pd.read_csv(HERE/'evaluacion_muestras.csv');f=pd.read_csv(HERE/'evaluacion_fuerzas.csv')
 s=d.groupby(['esquema','modelo']).mean(numeric_only=True)
 L=['# Validación temporal reservada: PASO 2021','',
 'Diputados nacionales, agrupados en cinco familias políticas; no pronostica las internas entre listas de una alianza. Porcentajes sobre votos positivos, que difieren del denominador oficial PASO de votos válidos cuando incluye blancos.',
 '', '**Estado:** se congeló el código antes de la prueba; se seleccionaron parámetros con 2017, se calibraron bandas con 2019 y se guardaron predicciones antes de abrir el resultado total PASO 2021. No se modificaron los parámetros después de evaluar este destino.',
 '', '**Límite de la ceguera:** esta es una reconstrucción retrospectiva con aislamiento de datos. La arquitectura, el catálogo de variantes y parte de los diseños ya fueron pensados con conocimiento de 2023/2025. La configuración congelada λ=0,1 y factor=1,4 también tiene esa influencia. La variante temporal vuelve a elegir sus constantes solo con resultados anteriores a septiembre de 2021. Ni esto ni otra semilla convierten la prueba en una predicción hecha en 2021.',
 '', '## Corte temporal y trazabilidad','',
 '- Código previo: `../congelado_20261028/codigo_congelado.zip`, 82 archivos verificados por SHA256; `ENTORNO.json` registra librerías y hash del ZIP.',
 '- `PROTOCOLO.md` y `PROTOCOLO_SELLADO.json`: decisiones y firmas previas a la evaluación. `PARAMETROS_SELLADOS.json`: selección/calibración terminadas antes de predecir 2021. `PREDICCIONES_SELLADAS.json`: hashes de las predicciones anteriores a la apertura del resultado.',
 '- El predictor utilizó solamente diputados generales 2019/2017, padrón reconstruido de claves/electores, y 30 actas reveladas por colección. No abrió las generales de noviembre de 2021 ni elecciones de 2023/2025 ni el total reservado de PASO 2021. Los accesos están en `accesos_prediccion.jsonl`.',
 '- Se comprobaron bloqueos del total reservado y de elecciones posteriores, ausencia de votos en el marco, 30 mesas únicas en las 700 selecciones y que Twitter parcial conserva las mismas mesas que Twitter completo (`CONTROLES.json`). Es una barrera de acceso en el proceso Python, no una garantía de aislamiento adversarial del sistema operativo.',
 '- Los datos se descargan hoy de archivos históricos: no se dispone de una copia de padrón y catálogos fechada antes del 12-sep-2021. Esos campos podían conocerse antes, pero esta reconstrucción no demuestra que cada versión actual del archivo sea idéntica a la publicada entonces.',
 '', 'Fuente oficial de PASO: [DINE, elecciones 2021](https://www.argentina.gob.ar/dine/resultados-electorales/elecciones-2021), ZIP `2021-provisorios_paso.zip`; URL y SHA256 en `../../datos_oficiales/2021_paso/FUENTE.json`.',
 '', '## Universo y clasificación','']
 meta=json.loads((HERE/'fuente_2021_paso.json').read_text())
 L+=['Marco territorial con electores nativos y padrón positivo: **%s mesas en %d distritos**, %s actas disponibles. Se contrasta contra los **%s votos positivos disponibles** de ese universo. No equivale al escrutinio definitivo ni garantiza cobertura de todos los inscriptos.'%(f"{meta['mesas_marco']:,}",meta['distritos'],f"{meta['actas_disponibles']:,}",f"{truth['votos_positivos']:,}"),
 '', 'La agrupación se fijó por nombres sin mirar sus votos: JXC, FDT, FIT, LIB y OTRAS. `config.py` y los CSV `mapeo_*.csv` muestran cada decisión. Las familias históricas son aproximaciones y no idénticas alianzas en todos los años. Por ejemplo, un partido nuevo sin antecedente propio se aprende a partir de las actas recibidas. No se eligieron fuerzas por superar un porcentaje del resultado final. No se incluye ICG, gobernadores, Zipf ni bancas: las PASO no asignan bancas.',
 '', '## Parámetros elegidos sin el destino','',
 'Se probaron λ=0,01; 0,1; 1 y swing (∞) en 2017, con antecedentes 2015/2013, 30 muestras por cada uno de siete diseños. Menor error medio por fuerza; desempate hacia mayor regularización.',
 '', '| λ | MAE por fuerza en 2017 |','|---|---:|']
 for key,value in cfg['scores_2017'].items():L.append('| %s | %.3f |'%(key,value))
 L+=['', '**Variante temporal fijada:** λ=%s; factor de banda **%.1f**. El factor se obtuvo solo con 2019 (antecedentes 2017/2015), a partir del cuantil 95 %% de la expansión necesaria del intervalo del margen, sin disminuirlo de 1.'%(cfg['lambda_temporal'],cfg['factor_temporal']),
 '', 'Esto es una única secuencia temporal de desarrollo→calibración→prueba, no muchas elecciones nuevas. La calibración histórica puede fallar si cambian el electorado, la oferta o la selección de mesas.',
 '', '## Diseños y comparaciones','',
 'Se evaluaron **700 colecciones de exactamente 30 mesas**, 100 por diseño, 200 remuestras de circuitos para cada modelo principal. Las mismas actas se usan para todas las variantes. Twitter contiene 20 mesas AMBA y 10 del resto, con racimos; la variante parcial oculta LIB/FIT/OTRAS en las primeras diez. El estrés partidario usa solo el perfil FDT del origen histórico; el geográfico usa tamaño de circuito, nunca el voto de 2021. La disponibilidad de actas se usa como metadato de recepción: se selecciona entre las que tienen algún resultado, sin elegir por partido.',
 '', 'Los baselines crudos calculan medias de proporciones observadas por fuerza (respetando faltantes), sin antecedentes; el ponderado agrega AMBA/resto. Swing emplea antecedentes y regularización infinita. Las ablaciones quitan un antecedente, el repesado o la regularización. No se elige una nueva configuración mirando qué ganó en este cuadro.',
 '', '| Diseño | Modelo | MAE fuerzas | MAE margen JXC−FDT | Sesgo del margen | MAE distrito | Ganadores /24 |','|---|---|---:|---:|---:|---:|---:|']
 for scheme in LABEL:
  for model in MODELS:
   r=s.loc[(scheme,model)]
   L.append('| %s | %s | %.3f | %.3f | %+.3f | %s | %s |'%(LABEL[scheme],model,r.mae_fuerzas,r.abs_error_margen,r.error_margen,'—' if not np.isfinite(r.mae_distrito) else '%.3f'%r.mae_distrito,'—' if not np.isfinite(r.ganadores_distrito) else '%.1f'%r.ganadores_distrito))
 L+=['','## Cobertura y ancho: modelos principales','',
 'Bandas nominales del 95 %. El intervalo Monte Carlo de cobertura usa Wilson para 100 colecciones condicionales a este conjunto electoral fijo; no expresa incertidumbre sobre futuras elecciones. Muestras de diferentes diseños pueden solaparse. El Brier de una sola elección, aun con muchas muestras, no certifica calibración probabilística.',
 '', '| Diseño | Modelo | Cobertura margen | IC Monte Carlo | Ancho medio | Inferencia disponible | Brier multiclase |','|---|---|---:|---|---:|---:|---:|']
 for scheme in LABEL:
  for model in ['congelado','temporal']:
   r=s.loc[(scheme,model)];lo,hi=wilson(r.cubre_margen,100)
   L.append('| %s | %s | %.0f %% | %.0f–%.0f %% | %.2f | %.0f %% | %.4f |'%(LABEL[scheme],model,100*r.cubre_margen,100*lo,100*hi,r.ancho_margen,100*r.inferencia_valida,r.brier))
 L+=['','### Error y cobertura por fuerza','',
 'Promedio de las 700 colecciones, con igual peso por diseño. La mezcla no sustituye los resultados separados por diseño; el detalle está en `evaluacion_fuerzas.csv`.',
 '', '| Fuerza | Modelo | MAE | Sesgo | Cobertura 95 % | Ancho medio |','|---|---|---:|---:|---:|---:|']
 fs=f[f.modelo.isin(['congelado','temporal'])].groupby(['fuerza','modelo'])[['abs_error','error','cubre','ancho']].mean()
 fs.to_csv(HERE/'resumen_fuerzas.csv')
 for (force,model),r in fs.iterrows():
  L.append('| %s | %s | %.3f | %+.3f | %.1f %% | %.2f |'%(force,model,r.abs_error,r.error,100*r.cubre,r.ancho))
 L+=['','**Fallo relevante:** en circuitos pequeños, LIB se proyectó en promedio en 1,406 % frente a 3,270 % observado. Su banda cubre solo el 29 % de las colecciones; también baja a 74 % en racimos y 68 % con sesgo histórico. La cobertura del margen JXC−FDT por sí sola ocultaría este problema. Bajo sesgo histórico, la cobertura del margen es 81 % con factor temporal 1,5, aun con un ancho medio de 27,6 puntos. No se corrigieron las bandas usando estos errores de 2021.',
 '', 'El MAE distrital promedia por igual los 24 distritos y las cinco fuerzas; no está ponderado por su tamaño. Los modelos secundarios no calculan bandas: su cobertura se deja vacía en los CSV. La enmienda documentada en `ENMIENDAS.md` corrige esa representación del evaluador; conserva todas las predicciones y los parámetros originales.',
 '', '## Resultado abierto después de predecir','', '| Fuerza | % del universo evaluado |','|---|---:|']
 for name,value in truth['nacional'].items():L.append('| %s | %.3f |'%(name,value))
 L+=['','Margen JXC−FDT: **%+.3f** puntos.'%truth['margen_JXC_FDT'],
 '', '### Primera colección de cada diseño (rep=0, no seleccionada por acierto)','',
 '| Diseño | Modelo | Margen proyectado | Error | Banda 95 % |','|---|---|---:|---:|---|']
 for scheme in LABEL:
  for model in ['congelado','temporal']:
   r=d[(d.esquema==scheme)&(d.modelo==model)&(d.rep==0)].iloc[0]
   L.append('| %s | %s | %+.2f | %+.2f | %+.2f a %+.2f |'%(LABEL[scheme],model,r.margen,r.error_margen,r.lo,r.hi))
   a=pd.read_json(HERE/'actas_reveladas'/('%s_000.json'%scheme),dtype={'distrito_id':str,'circuito':str,'mesa':str})
   a.to_csv(HERE/('ejemplo_30_'+scheme+'.csv'),index=False,encoding='utf-8-sig')
 # Comparaciones emparejadas; incertidumbre condicional, no de futuras elecciones.
 pairs=[];rng=np.random.default_rng(992021)
 for scheme in LABEL:
  x=d[(d.esquema==scheme)&(d.modelo=='congelado')].set_index('rep')
  for model in [v for v in MODELS if v!='congelado']:
   y=d[(d.esquema==scheme)&(d.modelo==model)].set_index('rep')
   diff=y.abs_error_margen-x.abs_error_margen
   ci=np.quantile(rng.choice(diff.to_numpy(),size=(3000,len(diff))).mean(1),[.025,.975])
   pairs.append(dict(esquema=scheme,modelo=model,delta_mae_margen_vs_congelado=diff.mean(),ic_mc_lo=ci[0],ic_mc_hi=ci[1]))
 pd.DataFrame(pairs).to_csv(HERE/'comparaciones_emparejadas.csv',index=False)
 # Resumen automático, sin una nueva selección de modelo.
 L+=['','## Lectura y límites','']
 for model in ['congelado','temporal']:
  a=s.xs(model,level='modelo');b=s.xs('swing',level='modelo');c=s.xs('crudo_ponderado',level='modelo')
  L.append('- %s: MAE del margen medio entre diseños %.3f; supera a swing en %d/7 diseños y al crudo ponderado en %d/7. Cobertura del margen entre %.0f %% y %.0f %%; ancho medio entre %.1f y %.1f puntos.'%(model,a.abs_error_margen.mean(),(a.abs_error_margen<b.abs_error_margen).sum(),(a.abs_error_margen<c.abs_error_margen).sum(),100*a.cubre_margen.min(),100*a.cubre_margen.max(),a.ancho_margen.min(),a.ancho_margen.max()))
 L+=['','La independencia temporal de los datos reduce la fuga directa y el ajuste de constantes al destino. No elimina la influencia del conocimiento previo al diseñar el método ni demuestra validez para toda elección. Una ventaja en esta PASO deberá reproducirse en otros destinos; una desventaja se conserva como resultado. Las bandas se juzgan junto con su ancho y no se recalibran con estos errores.',
 '', 'Las ablaciones tampoco dan una victoria universal a cada componente: en Twitter, quitar el repesado reduce el MAE del margen (3,683→3,186), pero empeora el MAE por fuerza (1,468→1,710). Se conserva la configuración fijada y se informa ese intercambio; no se selecciona una nueva variante con este destino.',
 '', 'Israel prueba otro sistema electoral y puede descubrir fallos de transporte, pero su estructura, oferta partidaria y mecanismos de llegada son distintos. No permite transferir automáticamente a Argentina su calibración de incertidumbre.',
 '', '**Siguiente evidencia necesaria:** evaluación con otras elecciones no utilizadas para diseñar variantes, y una corrida prospectiva con código congelado y predicciones guardadas antes de conocer el cierre. Esa prueba futura queda pendiente.',
 '', 'Referencias metodológicas: [Cawley y Talbot: sobreajuste en selección de modelos](https://www.jmlr.org/beta/papers/v11/cawley10a.html); [validación anidada, documentación oficial de scikit-learn](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).',
 '', '## Reproducción','', '```powershell',
 'python -X utf8 proyeccion/paso2021_ciego/descargar.py',
 'python -X utf8 proyeccion/paso2021_ciego/preparar.py',
 'python -X utf8 proyeccion/paso2021_ciego/calibrar.py',
 'python -X utf8 proyeccion/paso2021_ciego/custodio.py',
 'python -X utf8 proyeccion/paso2021_ciego/verificar_aislamiento.py',
 'python -X utf8 proyeccion/paso2021_ciego/predecir.py',
 'python -X utf8 proyeccion/paso2021_ciego/evaluar.py',
 'python -X utf8 proyeccion/paso2021_ciego/informe.py',
 '```','', 'No se debe volver a usar esta elección como prueba inédita después de haber leído este informe.',
 '', '![Comparación](comparacion_paso2021.png)','']
 (HERE/'RESULTADOS.md').write_text('\n'.join(L),encoding='utf8')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
 fig,axs=plt.subplots(1,2,figsize=(14,6),layout='constrained');y=np.arange(len(LABEL))
 for model,color in [('congelado','#166a88'),('temporal','#b04422'),('swing','#606a77')]:
  z=s.xs(model,level='modelo').reindex(LABEL)
  axs[0].plot(z.abs_error_margen,y,'o-',label=model,color=color)
  if model!='swing':axs[1].plot(100*z.cubre_margen,y,'o-',label=model,color=color)
 for ax in axs:
  ax.set_yticks(y,list(LABEL.values()));ax.invert_yaxis();ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.2)
 axs[0].set_xlabel('MAE del margen · puntos porcentuales');axs[0].set_title('Error: menos es mejor');axs[0].legend(frameon=False)
 axs[1].set_title('Cobertura del margen');axs[1].set_xlabel('% de colecciones que cubren el resultado');axs[1].set_xlim(0,102);axs[1].axvline(95,color='#888',linestyle='--')
 fig.suptitle('PASO 2021 reservada · 30 mesas · 100 colecciones por diseño',fontweight='bold',fontsize=15)
 fig.supxlabel('Parámetros temporales: elegidos en 2017, bandas calibradas en 2019.\nPrueba retrospectiva con aislamiento de datos; no prueba prospectiva.',fontsize=10)
 fig.savefig(HERE/'comparacion_paso2021.png',dpi=150)
 print('Informe y gráfico generados')

if __name__=='__main__':main()
