"""Usa el mismo flujo de descarga público que el visor (sin filtros territoriales)."""
from pathlib import Path
import requests,json,time
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
server=json.loads((META/'poblaciones_transaction.json').read_text(encoding='utf-8'))['Server']
session=requests.Session()
plan=json.loads((ROOT/'plan_descargas.json').read_text(encoding='utf-8'))
for boundary in [2,19]:
    j=json.loads((META/f'poblaciones_boundary{boundary}_real.json').read_text(encoding='utf-8'))
    for version in j['Versions']:
        ident=f'poblaciones_b{boundary}_v{version["Id"]}'
        params=dict(t='hw',s='b',b=boundary,v=version['Id'])
        statefile=META/(ident+'_download_state.json')
        state=json.loads(statefile.read_text(encoding='utf-8')) if statefile.exists() else None
        if not state:
            response=session.get(server+'/services/download/StartBoundaryDownload',params=params,timeout=(10,60));response.raise_for_status();state=response.json()
            statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        print(ident,'START',state,flush=True)
        for n in range(100):
            if state.get('done') is True:break
            if 'key' not in state:raise ValueError('Respuesta sin estado de trabajo: '+str(state))
            response=session.get(server+'/services/download/StepBoundaryDownload',params={'k':state['key']},timeout=(10,60));response.raise_for_status();state=response.json()
            statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
            print(ident,'STEP',n,state,flush=True)
        if state.get('done') is not True:raise ValueError('Trabajo no concluido')
        url=requests.Request('GET',server+'/services/download/GetBoundaryFile',params=params).prepare().url
        if not any(x['id']==ident for x in plan):
            plan.append(dict(id=ident,url=url,archivo=f'poblaciones/{j["Name"].replace(" ","_")}_{version["Name"]}.zip',tipo='municipio' if boundary==2 else 'gobierno local',corte=version['Name'],fuente=version['Metadata']['Ark'],nota='Descarga completa del visor público, versión identificada en metadata. No inferir que otro proveedor representa la misma delimitación.',licencia=version['Metadata']['License'],cobertura=version['Metadata']['Coverage']))
        (ROOT/'plan_descargas.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
