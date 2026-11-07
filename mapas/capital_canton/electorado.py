"""Estimación demográfica del electorado porteño según la regla de cada comicio."""
import csv
from bisect import bisect_left
from pathlib import Path

with Path(__file__).with_name("censos_ciudad.csv").open(encoding="utf-8", newline="") as archivo:
    CENSOS = {int(f["anio"]): f for f in csv.DictReader(archivo)}

ALONSO = "https://materiales.untrefvirtual.edu.ar/documentos_extras/1158_Problemas_de_historia_argentina/Alonso_entre_la_revolucion_y_las_urnas.pdf#page=10"
NACION = "https://www.argentina.gob.ar/normativa/nacional/"
REGLAS = {
    "75": ("Ley nacional 75 de 1863", NACION + "ley-75-281056/normas-modifican", 18),
    "623": ("Ley nacional 623 de 1873", NACION + "ley-623-281565", 17),
    "893": ("Ley nacional 893 de 1877 y modificatorias", NACION + "ley-893-283832", 17),
    "p1854": ("Constitución bonaerense de 1854, arts. 6–7", "https://www.hcdiputados-ba.gov.ar/index.php?id=2&page=normativas&section=constitucionProvincial", 21),
    "p1067": ("Ley bonaerense 1067 de 1876, art. 12", "https://normas.gba.gob.ar/documentos/Byd95Flx.pdf", 17),
    "4161": ("Ley nacional 4161 de 1902", "https://cdi.mecon.gov.ar/bases/docelec/az2453.pdf", 18),
    "4578": ("Ley nacional 4161 con reformas de 1905", NACION + "ley-4578-286016", 18),
    "8871": ("Ley nacional 8871 de 1912", NACION + "ley-8871-310143/texto", 18),
    "13010": ("Ley nacional 13.010 de 1947", NACION + "ley-13010-47353/texto", 18),
    "14032": ("Ley nacional 14.032 de 1951", NACION + "ley-14032-296397/texto", 18),
    "4034": ("Estatuto electoral de 1957 y normas complementarias", NACION + "decreto_ley-4034-1957-297184/normas-modifican", 18),
    "19945": ("Código Electoral Nacional, Ley 19.945", NACION + "ley-19945-19442/texto", 18),
    "24620": ("Ley nacional 24.620, art. 4", NACION + "ley-24620-31825/texto", 18),
    "334": ("Ley porteña 334 de 2000 y Código Electoral Nacional", "https://boletinoficial.buenosaires.gob.ar/normativaba/norma/6180", 18),
}


def _regla(n, anio):
    if n in (2, 3):
        return "p1854"
    if n in (6, 8):
        return "p1067"
    if n in (88, 89):
        return "24620"
    if n in (93, 94, 99, 100, 101, 103, 104, 105):
        return "334"
    return next(clave for inicio, clave in (
        (1973, "19945"), (1957, "4034"), (1951, "14032"), (1948, "13010"),
        (1912, "8871"), (1906, "4578"), (1904, "4161"), (1877, "893"),
        (1874, "623"), (1864, "75"),
    ) if anio >= inicio)


def _censo(anio, edad, sexos, ciudad_antigua):
    f = CENSOS[anio]
    pob = int(f["poblacion"])
    pot = {}
    for s in sexos:
        personas = int(f[f"{s}_20_mas"])
        if edad < 20:
            personas += (20 - edad) / 5 * int(f[f"{s}_15_19"])
        else:
            personas -= (edad - 20) / 5 * int(f[f"{s}_20_24"])
        pot[s] = personas
    if anio == 1887 and edad in (17, 18) and sexos == "V":
        # Censo municipal de 1887, t. II, p. 38. Edades simples.
        pot["V"] = int(f["V_20_mas"]) + 2074 + 1606 + (2075 if edad == 17 else 0)
    if ciudad_antigua and anio in (1869, 1887):
        recorte = {1869: 177787, 1887: 407990}[anio]
        pot = {s: v * recorte / pob for s, v in pot.items()}
        pob = recorte
    if anio == 1970:
        # El cuadro 1.23 suma 2.905.750. Se aplican sus proporciones al total censal.
        pot = {s: v * 2972453 / pob for s, v in pot.items()}
        pob = 2972453
    return {**pot, "pob": pob}


def estimar(n, anio):
    clave = _regla(n, anio)
    ley, enlace, edad = REGLAS[clave]
    sexos = "V" if anio < 1951 else "VM"
    grupo = "varones" if sexos == "V" else "varones y mujeres"
    edad_texto = "mayores de 17 años" if edad == 17 else f"desde los {edad} años"
    salida = {"ley": ley, "enlace": enlace, "regla": f"Ciudadanos argentinos {edad_texto} ({grupo})."}
    if clave == "334":
        salida["regla"] = "Ciudadanos argentinos desde los 18 años y extranjeros desde los 18 con residencia permanente y tres años en la ciudad."
        salida["reserva"] = "Los cuadros censales no identifican el conjunto de extranjeros que cumple las condiciones de residencia. Falta un denominador comparable para el padrón local."
        return salida
    if clave == "p1854":
        salida["regla"] = "Umbral general de 21 años. También podían votar menores enrolados en la Guardia Nacional y casados mayores de 18."
        salida["reserva"] = "La base censal de 21 años y más cubre el umbral general. El censo no permite agregar los menores habilitados por las excepciones."
        salida["parcial"] = True
    if clave == "13010":
        salida["regla"] = "La ley reconocía el sufragio de las mujeres. El padrón femenino se aplicó por primera vez en 1951. Para estas elecciones de 1948 se usa la base masculina."

    if 1890 <= anio <= 1898:
        salida.update(censo="1895", poblacion=663854, valores={"T": 51089}, fuentes=[ALONSO], publicada=True)
        if n == 21:
            salida["reserva"] = "La planilla 21 de Cantón y Jorrat registra 21.317 inscriptos. Alonso estudia un registro de 24.200 inscriptos, con otra cobertura parroquial."
        return salida

    anios = [1855, 1869, 1887] if anio < 1887 else [a for a in CENSOS if a >= 1904]
    i = bisect_left(anios, anio)
    antes, despues = (anios[i], anios[i]) if anios[i] == anio else (anios[i - 1], anios[i])
    izquierda = _censo(antes, edad, sexos, anio < 1887)
    derecha = _censo(despues, edad, sexos, anio < 1887)
    fraccion = (anio - antes) / (despues - antes) if despues != antes else 0
    valores = {s: round(izquierda[s] + (derecha[s] - izquierda[s]) * fraccion) for s in sexos}
    fuentes = [CENSOS[a]["fuente"] for a in dict.fromkeys((antes, despues))]
    if 1887 in (antes, despues):
        fuentes.append("https://biblioteca.indec.gob.ar/bases/minde/1cf1887t2.pdf")
    salida.update(censo=str(antes) if antes == despues else f"{antes}–{despues}",
                  poblacion=round(izquierda["pob"] + (derecha["pob"] - izquierda["pob"]) * fraccion),
                  valores={"T": sum(valores.values()), **valores}, fuentes=fuentes)
    if n == 24:
        salida["reserva"] = "El padrón de esta elección cubre once circunscripciones. La estimación censal corresponde a toda la ciudad."
        salida["parcial"] = True
    return salida
