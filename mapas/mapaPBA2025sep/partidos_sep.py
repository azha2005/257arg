"""Agrupaciones, nombres y colores del 7-sep-2025 (comunes a los atlas de esta carpeta).
Bloques como la tabla de la Wikipedia (Elecciones provinciales de Buenos Aires de 2025, wpba2025.txt): Somos Buenos Aires suma
«Espacio Abierto para el Desarrollo y la Integración Social», lista ligada en la tabla. Colores: FP, LLA y FIT como el atlas
legislativo 2025 del proyecto (un partido se ve igual en todos los atlas); Somos con el rosa #FE9AC3 de la Wikipedia."""
import re, unicodedata

BLOCS = ["FP", "LLA", "SB", "FIT"]
COLOR = dict(FP="#009ce4", LLA="#6c4c98", SB="#FE9AC3", FIT="#f65058")
LABEL = dict(FP="Fuerza Patria", LLA="La Libertad Avanza", SB="Somos Buenos Aires", FIT="Frente de Izquierda y de Trabajadores - Unidad")


def bloc_of(n):
    n = str(n)
    if n == "FUERZA PATRIA": return "FP"
    if n == "LA LIBERTAD AVANZA": return "LLA"
    if n in ("SOMOS BUENOS AIRES", "ESP. ABIERTO PARA EL DES. Y LA INT. SOCIAL"): return "SB"
    if n == "FTE DE IZQ. Y DE TRABAJADORES - UNIDAD": return "FIT"
    return None


def slug(n):
    n = unicodedata.normalize("NFD", str(n).lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", n).strip("_")[:40]


def title(n):
    return str(n).title().replace(" De ", " de ").replace(" Del ", " del ").replace(" Y ", " y ").replace(" La ", " la ").replace(" El ", " el ")
