from pathlib import Path
import requests,json
s=requests.Session();s.headers['User-Agent']='DataeleccAtlas/1.0 (https://commons.wikimedia.org/wiki/User:ItsAHardLife)'
obj=s.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',titles='File:Concertación Justicialista para el Cambio.png',prop='imageinfo',iiprop='url|extmetadata',format='json'),timeout=60).json()
p=next(iter(obj['query']['pages'].values()));info=p['imageinfo'][0]
Path('mapa1999dip/logo_cjc_metadata.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
data=s.get(info['url'],timeout=60);data.raise_for_status();Path('logos_wikipedia/Concertacion_Justicialista_1999.png').write_bytes(data.content)
print(info['url']);print(info['extmetadata'].get('DateTimeOriginal'))
