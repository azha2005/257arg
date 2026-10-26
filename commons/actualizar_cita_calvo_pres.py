"""Actualiza los textos locales sin borrar las planillas fuente ni regenerar mapas."""
from pathlib import Path
from config import CALVO, CALVO_PRES_CITA

root = Path(__file__).parent
for year in ('1983', '1989'):
    old = CALVO.format(xls=f'TPDENP{year}T.xls', cargo='presidente')
    paths = list((root / year / 'subir').glob('*.txt'))
    paths.append(root / year / 'LEEME_SUBIDA.md')
    for path in paths:
        text = path.read_text(encoding='utf-8')
        if old in text:
            path.write_text(text.replace(old, CALVO_PRES_CITA), encoding='utf-8')
            print(path.name)
