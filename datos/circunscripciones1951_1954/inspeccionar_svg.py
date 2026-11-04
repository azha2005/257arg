from pathlib import Path
import xml.etree.ElementTree as ET
from svgelements import SVG, Path as SVGPath
HERE=Path(__file__).resolve().parent
root=ET.parse(HERE/'circunscripciones_1951.svg').getroot()
parsed=SVG.parse(str(HERE/'circunscripciones_1951.svg'),parse_display_none=True)
paths={p.id:p for p in parsed.elements() if isinstance(p,SVGPath)}
L='{http://www.inkscape.org/namespaces/inkscape}label'
layer=next(e for e in root if e.get('id')=='layer2')
for e in layer:
    print(e.get('id'),e.get(L))
    if e.get(L) == 'Provincia de Buenos Aires':
        for x in e:
            print(' ',x.get(L),[(k.get('id'),tuple(round(c,1) for c in paths[k.get('id')].bbox())) for k in x.iter() if k.get('id') in paths])
