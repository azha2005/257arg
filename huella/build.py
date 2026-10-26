"""huella.json + plantilla.html -> huella_1916_1928.html"""
import os
D = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(D, 'plantilla.html'), encoding='utf-8').read().replace(
    '/*DATA*/[]', open(os.path.join(D, 'huella.json'), encoding='utf-8').read())
open(os.path.join(D, 'huella_1916_1928.html'), 'w', encoding='utf-8').write(html)
print('escrito huella_1916_1928.html', len(html) // 1024, 'KB')
