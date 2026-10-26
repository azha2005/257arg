from head_amba import *
used = set(UKEYS)
secs = {(k[0], k[1]) for k in target}  # (dist, sec) del AMBA en la base
amba_secs = {s for s in secs if s[0] == '02'}
unm = [k for k in feats if k[0]=='02' and ('02',k[1]) in amba_secs and k not in used]
print('poligonos AMBA sin datos:', len(unm), 'de', sum(1 for k in feats if k[0]=='02' and ('02',k[1]) in amba_secs))
print(collections.Counter(part_of[('02',k[1])] for k in unm).most_common(12))
print(sorted(k[2] for k in unm)[:40])
# estan los datos de esos circuitos bajo otra clave?
dd = collections.Counter()
for k in unm:
    sec=k[1]; cands=[c for c in target if c[0]=='02' and c[1]==sec]
    dd[sec]=len(cands)
print([ (k, [c[2] for c in target if c[0]=='02' and c[1]==k[1]][:12]) for k in unm[:3]])
