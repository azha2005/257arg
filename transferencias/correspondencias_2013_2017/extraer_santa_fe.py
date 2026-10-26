"""Tabla oficial anterior -> nueva del anexo de la Res. CNE 66/2022."""
from pathlib import Path
import re
import pandas as pd
import pymupdf

HERE = Path(__file__).resolve().parent
OLD_SECTION = {17: 1, 14: 2, 5: 3, 15: 4, 4: 5, 16: 6, 9: 7, 18: 8, 1: 9, 2: 11,
               12: 12, 13: 13, 7: 16, 11: 17, 3: 18, 8: 19, 19: 20, 6: 21, 10: 22}

rows = []
for page in pymupdf.open(HERE / "sf_res66_2022_anexo1.pdf"):
    if page.number == 0:
        continue
    for table in page.find_tables().tables:
        for row in table.extract():
            if len(row) != 7 or not row[0] or not row[2] or not row[5]:
                continue
            old, new = row[0].strip(), row[2].strip()
            if not re.fullmatch(r"\d+[A-Z]?", old) or not new.isdigit() or not row[5].strip().isdigit():
                continue
            section = int(row[5].strip())
            rows.append(dict(seccion_anterior=OLD_SECTION[section], circuito_anterior=old,
                             nombre_anterior=row[1], seccion_nueva=section, circuito_nuevo=new,
                             nombre_nuevo=row[3], pagina=page.number + 1, fuente_id="sf_res66_2022"))
result = pd.DataFrame(rows).drop_duplicates()
assert not result.duplicated(["seccion_anterior", "circuito_anterior"]).any()
assert not result.duplicated(["seccion_nueva", "circuito_nuevo"]).any()
result.to_csv(HERE / "santa_fe_2022.csv", index=False, encoding="utf-8-sig")
print(len(result), "equivalencias oficiales")
