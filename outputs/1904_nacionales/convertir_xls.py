"""Conversión BIFF8: capacidad XLS no disponible en Artifact Tool.

Conserva los valores históricos calculados y comprobados por el autor JS.
"""
from pathlib import Path
import json,xlwt,xlrd
p=Path(__file__).resolve().parent
values=json.loads((p/'valores.json').read_text(encoding='utf8'))
w=xlwt.Workbook(encoding='utf-8');s=w.add_sheet('Resultados 1904');s.show_grid=False
s.col(0).width=74*256;s.col(1).width=16*256;s.col(2).width=22*256
base=xlwt.easyxf('font: name Arial, height 200; align: vert centre;')
number=xlwt.easyxf('font: name Arial, height 200; align: horiz right, vert centre;',num_format_str='#,##0')
percent=xlwt.easyxf('font: name Arial, height 200; align: horiz right, vert centre;',num_format_str='0.00%')
title=xlwt.easyxf('font: name Arial, height 280, bold on;')
header=xlwt.easyxf('font: name Arial, height 200, bold on, colour white; pattern: pattern solid, fore_colour dark_blue; align: horiz center, vert centre;')
total=xlwt.easyxf('font: name Arial, height 200, bold on; borders: top thin;')
tn=xlwt.easyxf('font: name Arial, height 200, bold on; borders: top thin; align: horiz right;',num_format_str='#,##0')
tp=xlwt.easyxf('font: name Arial, height 200, bold on; borders: top thin; align: horiz right;',num_format_str='0.00%')
for r,row in enumerate(values):
    s.row(r).height=22*20
    for c,value in enumerate(row):
        if value is None:continue
        style=title if r==1 else header if r==4 else (total,tn,tp)[c]if r==15 else percent if c==2 and 5<=r<=14 else number if c==1 and 5<=r<=14 else base
        s.write(r,c,value,style)
circs=json.loads((p/'circ_valores.json').read_text(encoding='utf8'))
cs=w.add_sheet('Por circunscripción');cs.show_grid=False
cs.panes_frozen=True;cs.horz_split_pos=1
for i,width in enumerate([23,9,24,32,44,20,18,18,10,40]):cs.col(i).width=width*256
for r,row in enumerate(circs):
    cs.row(r).height=(32 if r==0 else 22)*20
    for c,value in enumerate(row):
        if value is not None:cs.write(r,c,value,header if r==0 else percent if c==7 else number if c in (1,6)else base)
target=p/'Resultados_nacionales_1904.xls'
old=xlrd.open_workbook(target).sheet_by_index(0)
original=[[old.cell_value(r,c)for c in range(old.ncols)]for r in range(old.nrows)]
w.save(str(target))
check=xlrd.open_workbook(target).sheet_by_index(0)
assert sum(check.cell_value(r,1)for r in range(5,15))==check.cell_value(15,1)==129796
assert abs(check.cell_value(15,2)-1)<1e-10
assert target.read_bytes()[:8]==bytes.fromhex('D0CF11E0A1B11AE1')
for r,row in enumerate(values):
    for c,v in enumerate(row):
        if v is not None:assert check.cell_value(r,c)==v,(r,c,v)
print('XLS BIFF8 verificado:',target)
for r,row in enumerate(original):
    for c,v in enumerate(row):assert check.cell_value(r,c)==v
detail=xlrd.open_workbook(target).sheet_by_index(1)
assert detail.nrows==len(circs)
assert sum(detail.cell_value(r,6)or 0 for r in range(1,detail.nrows))==129796
assert len({(detail.cell_value(r,0),detail.cell_value(r,1))for r in range(1,detail.nrows)})==120
print('Resumen conservado; detalle de 120 circunscripciones verificado.')
