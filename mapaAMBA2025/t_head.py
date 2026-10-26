import sys
sys.argv=['x']
from head_amba import *
print(len(UKEYS), len(PARTIDOS), 'unidades; bbox px', shapely.total_bounds(G_raw))
c=collections.Counter((r.get('w') or 'fill') for r in unit_rec.values()); print(c)
print({b:round(100*TOT['bloc'][b]/TOT['pos'],2) for b in BLOCS}, 'part', round(100*TOT['E']/TOT['elok'],2))
print([(disp[i],unit_rec[i]['note'][:70]) for i in range(len(UKEYS)) if unit_rec[i].get('fill')==BEIGE][:5])
