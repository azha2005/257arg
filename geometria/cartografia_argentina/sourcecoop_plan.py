from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent;p=ROOT/'plan_descargas.json';plan=json.loads(p.read_text(encoding='utf-8'))
for year in [1991,2001,2010,2022]:
    for file in ['radios.parquet','collection.json','README.md']:
        ident='sourcecoop_'+str(year)+'_'+file
        if any(r['id']==ident for r in plan):continue
        plan.append(dict(id=ident,url=f'https://data.source.coop/nlebovits/censo-argentino/{year}/{file}',archivo=f'source_cooperative/{year}/{file}',tipo='radio censal (derivado GeoParquet)',corte=str(year),cobertura='Argentina',fuente=f'https://source.coop/nlebovits/censo-argentino/{year}',nota='Nissim Lebovits declara geometrías Rodríguez/De Grande CONICET reproyectadas a EPSG:4326. Es un derivado de CEUR, no una nueva fuente independiente de límites.',licencia='CC BY 4.0 declarada por repositorio; mantener atribución INDEC/CONICET/Lebovits y condiciones originales.'))
p.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
