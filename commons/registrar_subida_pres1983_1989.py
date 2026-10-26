"""Conserva la reserva publicada sobre Malargüe en los wikitext locales."""
from pathlib import Path

NOTE = ('* Reserva sobre Malargüe (Mendoza): este mapa conserva FREJUPO 3.864 y UCR 3.912 de la base de Ernesto Calvo (ganador: Angeloz). La transcripción de UNCuyo registra FREJUPO 3.964; con esa cifra el ganador es Menem. La discrepancia no está resuelta y debe tenerse en cuenta al reutilizar el mapa.\n')

for path in (Path(__file__).parent / '1989' / 'subir').glob('*.txt'):
    content = path.read_text(encoding='utf-8')
    if NOTE.strip() not in content:
        content = content.replace('|author=', NOTE + '|author=', 1)
        path.write_text(content, encoding='utf-8')
