import requests,re,json
from pathlib import Path
s=requests.Session();s.headers['User-Agent']='DataeleccAtlas/1.0 (https://commons.wikimedia.org/wiki/User:ItsAHardLife)'
t=s.get('https://es.wikipedia.org/w/api.php',params=dict(action='parse',page='Cruzada Renovadora',prop='wikitext',format='json'),timeout=60).json()['parse']['wikitext']['*']
Path('mapas/mapa1989dip/cruzada_wiki.txt').write_text(t,encoding='utf8')
print(t[:1700].encode('ascii','backslashreplace').decode())
