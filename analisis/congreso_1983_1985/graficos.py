"""Hemiciclos estáticos de los escenarios, hechos exclusivamente con código."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE/'resultado.json').read_text(encoding='utf8'))
COLORS = {'UCR':'#e10019', 'PJ':'#318ce7', 'Otros':'#939393'}
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'path'})

def totals(field):
    out = {'UCR':0,'PJ':0,'Otros':0}
    for r in DATA['summary']:
        out[r['party'] if r['party'] in ('UCR','PJ') else 'Otros'] += r[field]
    assert sum(out.values()) == 254
    return out

def draw(ax,year):
    count = totals('total1983' if year==1983 else 'total1985_illustrative')
    seats = []
    # Siete filas: cada punto representa una banca, sin posiciones superpuestas.
    for n,radius in zip([23,28,32,36,41,45,49],np.linspace(.5,1.1,7)):
        for angle in np.linspace(np.pi,0,n):
            seats.append((angle,radius,radius*np.cos(angle),radius*np.sin(angle)))
    seats.sort(key=lambda s:(-s[0],s[1]))
    order = ['UCR','Otros','PJ']
    colors = [COLORS[c] for c in order for _ in range(count[c])]
    assert len(colors)==len(seats)==254
    ax.scatter([s[2] for s in seats],[s[3] for s in seats],s=49,c=colors,
               edgecolors='white',linewidths=.5,zorder=3)
    ax.set_aspect('equal')
    ax.set_xlim(-1.25,1.25);ax.set_ylim(-.47,1.47);ax.axis('off')
    ax.text(0,1.40,str(year),ha='center',va='center',fontsize=30,weight='bold',color='#333333')
    ax.text(0,1.23,'Cámara de Diputados',ha='center',fontsize=15,color='#555555')
    win = 'PJ' if year==1983 else 'UCR'
    ax.text(0,.29,str(count[win]),ha='center',fontsize=37,weight='bold',color=COLORS[win])
    ax.text(0,.15,f'{win} · mayoría propia',ha='center',fontsize=11,weight='bold',color='#444444')
    ax.text(0,.025,'254 bancas · mayoría: 128',ha='center',fontsize=10,color='#666666')
    labels=[f'UCR  {count["UCR"]}',f'Peronismo  {count["PJ"]}',f'Otras fuerzas  {count["Otros"]}']
    handles=[Line2D([],[],marker='o',linestyle='',color=COLORS[c],markersize=8) for c in ('UCR','PJ','Otros')]
    ax.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.12),ncol=3,
              frameon=False,fontsize=10,handletextpad=.2,columnspacing=1.1)
    if year==1983:
        note='Hipótesis: mismo voto provincial para Presidente y Diputados.'
    else:
        note='Composición estimada: 127 nuevos + 127 que continúan de 1983.'
    ax.text(0,-.30,note,ha='center',fontsize=9,color='#666666')
    if year==1985:
        ax.text(0,-.39,'Reparto equilibrado de mandatos: UCR entre 132 y 134 bancas.',ha='center',fontsize=9,color='#666666')

for year in (1983,1985):
    fig,ax=plt.subplots(figsize=(10,8),facecolor='white')
    draw(ax,year)
    fig.subplots_adjust(left=.025,right=.975,top=.96,bottom=.05)
    fig.text(.5,.022,'ESCENARIO HIPOTÉTICO · D’Hondt por distrito · Un punto = una banca',
             ha='center',fontsize=9,color='#777777')
    for ext in ('png','svg'):
        fig.savefig(HERE/f'diputados_{year}_hipotetico.{ext}',dpi=200,facecolor='white')
    plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(16,7),facecolor='white')
for ax,year in zip(axes,(1983,1985)):draw(ax,year)
fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.07,wspace=.10)
fig.text(.5,.025,'ESCENARIOS HIPOTÉTICOS · D’Hondt por distrito · Un punto = una banca · Senado no simulado',
         ha='center',fontsize=10,color='#777777')
for ext in ('png','svg'):
    fig.savefig(HERE/f'diputados_1983_1985.{ext}',dpi=180,facecolor='white')
plt.close(fig)
print(HERE/'diputados_1983_1985.png')
