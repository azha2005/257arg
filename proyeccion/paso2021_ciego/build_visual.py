from pathlib import Path
import json,sys,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge,Polygon,Circle
P=Path('proyeccion/paso2021_ciego');sys.path.insert(0,'proyeccion');import congreso as cg
F=['JXC','FDT','FIT','LIB','OTRAS'];C={'JXC':'#d6a211','FDT':'#009ce4','FIT':'#ed4d57','LIB':'#6c4c98','OTRAS':'#929292'}
N={'JXC':'Juntos por el Cambio','FDT':'Frente de Todos','FIT':'FIT-Unidad','LIB':'Liberales','OTRAS':'Otras fuerzas'}
S={'azar':'Azar','padron_distrito':'Proporcional al padrón','racimos':'Diez circuitos × tres mesas','twitter':'Tipo Twitter · 20 AMBA / 10 resto','twitter_parcial':'Twitter · diez actas parciales','geografico':'Circuitos pequeños','sesgo_historico':'Sesgo según voto histórico'}
D={}
for k in S:
 r=next(x for x in json.loads((P/'predicciones'/f'{k}.json').read_text(encoding='utf8')) if x['modelo']=='temporal' and x['rep']==0);D[k]=r
real=json.loads((P/'REAL_ABIERTO.json').read_text());r=D['twitter'];m=r['margen'];lo,hi=r['margen_banda'];a=lambda x:90-90*np.clip(x/30,-1,1)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig=plt.figure(figsize=(9,10),facecolor='white');fig.text(.06,.96,'PASO 2021 · proyección con 30 mesas',fontsize=21,weight='bold');fig.text(.06,.925,'Primera colección tipo Twitter · antecedentes 2019 + 2017',fontsize=11,color='#666')
ax=fig.add_axes([.08,.48,.84,.39]);ax.set(xlim=(-1.2,1.2),ylim=(-.45,1.18));ax.set_aspect('equal');ax.axis('off')
for side,col in [(-1,C['FDT']),(1,C['JXC'])]:
 for i,(l,h) in enumerate([(1,5),(5,15),(15,30)]):
  aa,bb=sorted([a(side*l),a(side*h)]);ax.add_patch(Wedge((0,0),1,aa,bb,width=.4,facecolor=col,alpha=.4+i*.3,edgecolor='white',linewidth=2))
ax.add_patch(Wedge((0,0),1,a(1),a(-1),width=.4,facecolor='#ddd',edgecolor='white'));ax.text(0,1.12,'EMPATE',ha='center',color='#777',fontsize=9)
for x in [-30,-20,-10,10,20,30]:
 t=np.radians(a(x));ax.plot([np.cos(t),1.04*np.cos(t)],[np.sin(t),1.04*np.sin(t)],color='#888',lw=1);ax.text(1.12*np.cos(t),1.12*np.sin(t),'+'+str(abs(x)),ha='center',va='center',color='#777')
aa,bb=sorted([a(lo),a(hi)]);ax.add_patch(Wedge((0,0),.57,aa,bb,facecolor='#555',alpha=.18));t=np.radians(a(m));v=np.array([-np.sin(t),np.cos(t)])*.025;tip=np.array([.97*np.cos(t),.97*np.sin(t)]);ax.add_patch(Polygon([tip,v,-v],color='#151515'));ax.add_patch(Circle((0,0),.05,color='#151515'))
for side,f,j in [(-1,'FDT',1),(1,'JXC',0)]:
 ha='left' if side<0 else 'right';ax.text(side,-.07,('Frente de\nTodos' if f=='FDT' else 'Juntos por\nel Cambio'),ha=ha,va='top',color=C[f],weight='bold',fontsize=11);ax.text(side,-.30,f'{100*r["prob_primero"][j]:.0f} %',ha=ha,color=C[f],fontsize=22,weight='bold');ax.text(side,-.43,'primero en las remuestras',ha=ha,color='#777',fontsize=8)
ax.text(0,-.14,f'JXC +{m:.1f}',ha='center',weight='bold',fontsize=18,color=C['JXC']);ax.text(0,-.29,f'Banda 95 %: {lo:+.1f} a {hi:+.1f}',ha='center',fontsize=9,color='#666')
fig.text(.06,.455,' · '.join(f'{f} {r["punto"][i]:.1f} %' for i,f in enumerate(F)),fontsize=10,weight='bold')
bx=fig.add_axes([.29,.17,.64,.25]);yy=np.arange(7)
for i,k in enumerate(S):
 x=D[k];l,h=x['margen_banda'];bx.plot([l,h],[i,i],color='#c9c9c9',lw=6,solid_capstyle='round');bx.scatter(x['margen'],i,color=C['JXC'],zorder=3)
bx.set_yticks(yy,list(S.values()),fontsize=8);bx.invert_yaxis();bx.axvline(real['margen_JXC_FDT'],ls='--',color='#555',label='Resultado: JXC +8,48');bx.axvline(0,color='#bbb',lw=.8);bx.set_xlabel('Margen JXC − FDT · primera colección de cada diseño');bx.spines[['top','right','left']].set_visible(False);bx.legend(frameon=False,fontsize=8,loc='upper right')
fig.text(.06,.065,'Reconstrucción retrospectiva; cada diseño usa 30 mesas, no una secuencia horaria.\nBandas nominales: bootstrap de circuitos ×1,5, calibrado con 2019.\nLa selección sesgada puede quedar fuera de estas bandas. Las PASO no asignan bancas.',fontsize=9,color='#666',linespacing=1.5)
fig.savefig(P/'aguja_paso2021.png',dpi=160,bbox_inches='tight');plt.close(fig)
geo=json.loads(Path('proyeccion/provincias_svg.json').read_text());inv={v:k for k,v in cg.DIST.items()};paths={inv[n]:d for n,d in geo.items() if n in inv};b=np.array([cg._bbox(d) for d in paths.values()]);view=[b[:,0].min()-10,b[:,1].min()-10,b[:,2].max()-b[:,0].min()+50,b[:,3].max()-b[:,1].min()+20]
payload={'samples':D,'schemes':S,'forces':F,'colors':C,'names':N,'real':real,'districts':cg.DIST,'paths':paths,'view':view};(P/'visual_datos.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf8')
print('PNG y datos visuales generados')
