"""Último intento acotado de recuperar los PDF oficiales citados por Wikipedia."""
from fuentes_leg2003_2025 import OUT,UA
import urllib.request
sources={
 'la_pampa_2003_archivo.pdf':'https://web.archive.org/web/20110902183839id_/http://www.elecciones.gob.ar/estadistica/archivos/2003/La_Pampa/La_PampaSENyDIPnac.pdf',
 'la_pampa_2005_archivo.pdf':'https://web.archive.org/web/20110902185823id_/http://www.elecciones.gob.ar/estadistica/archivos/2005/La_Pampa_23_Oct_2005.pdf',
 'jujuy_2005_archivo.pdf':'https://web.archive.org/web/20110902183436id_/http://www.elecciones.gob.ar/estadistica/archivos/2005/Jujuy_23_Oct_2005.pdf',
}
for name,url in sources.items():
    try:
        data=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=20).read()
        if data.startswith(b'%PDF'):(OUT/name).write_bytes(data);print('OK',name,len(data),flush=True)
        else:print('NO PDF',name,flush=True)
    except Exception as e:print('FAILED',name,str(e),flush=True)
