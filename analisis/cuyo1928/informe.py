"""resultados.json + plantilla.html -> informe_cuyo1928.html"""
import os
D = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(D, 'plantilla.html'), encoding='utf-8').read().replace(
    '/*DATA*/null', open(os.path.join(D, 'resultados.json'), encoding='utf-8').read())
open(os.path.join(D, 'informe_cuyo1928.html'), 'w', encoding='utf-8').write(html)
print('escrito informe_cuyo1928.html', len(html) // 1024, 'KB')
