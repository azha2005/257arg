from pathlib import Path
from urllib.parse import urljoin
import requests,json,concurrent.futures as cf
ROOT=Path(__file__).resolve().parent; META=ROOT/'metadatos'
jobs=[('dspace_config','https://ri.conicet.gov.ar/res/assets/config.f76c44c49916c3cb7bc6cd4193681118.json'),('radios_ceur2010_config','https://raw.githubusercontent.com/matuteiglesias/argentina-geography/main/config/sources/ceur_census_2010_radio_v2025_1.json'),('radios_ceur2022_config','https://raw.githubusercontent.com/matuteiglesias/argentina-geography/main/config/sources/ceur_census_2022_radio_v2025_1.json'),('radios_indec2010_config','https://raw.githubusercontent.com/matuteiglesias/argentina-geography/main/config/sources/indec_census_2010_radio.json'),('radios_indec2022_config','https://raw.githubusercontent.com/matuteiglesias/argentina-geography/main/config/sources/indec_census_2022_radio.json'),('poblaciones_municipios','https://poblaciones.org/2025/12/22/municipios-y-otras-formas-de-gobiernos-locales-2022/'),('dspace_find_radios','https://ri.conicet.gov.ar/server/api/pid/find?id=11336/149711'),('dspace_find_deptos','https://ri.conicet.gov.ar/server/api/pid/find?id=11336/149867')]
def f(a):
    name,u=a
    try:
        r=requests.get(u,timeout=(10,35));(META/(name+'.txt')).write_text(r.text,encoding='utf-8');print(name,r.status_code,len(r.content),r.text[:6500] if name.endswith('config') else r.text[:250],flush=True)
    except Exception as e:print(name,e,flush=True)
with cf.ThreadPoolExecutor(6) as ex:list(ex.map(f,jobs))
