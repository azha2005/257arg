"""Inserta resultados.json en plantilla.html -> informe_sanjuan.html"""
import os
D = os.path.dirname(os.path.abspath(__file__))
data = open(os.path.join(D, 'resultados.json'), encoding='utf-8').read()
html = open(os.path.join(D, 'plantilla.html'), encoding='utf-8').read().replace('/*DATA*/null', data)
open(os.path.join(D, 'informe_sanjuan.html'), 'w', encoding='utf-8').write(html)
print('escrito informe_sanjuan.html', len(html) // 1024, 'KB')
