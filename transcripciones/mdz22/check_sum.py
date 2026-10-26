# Let's sum the totals from pages 325-335:
depts = {
    "Capital": 213,
    "Las Heras": 37,
    "Guaymallen": 46,
    "Godoy Cruz": 71,
    "Maipu": 31,
    "Lujan": 131,
    "San Martin": 108,
    "Rivadavia": 107,
    "Gral. Alvear": 33,
    "Tupungato": 23,
    "Lavalle": 42,
    "San Rafael": 44,
    "Santa Rosa / La Paz / Tunuyan / San Carlos / Junin": 0 # let's check
}

print("Sum of listed departments:", sum(depts.values()))
print("Page 335 stated total:", 966)
print("Difference:", 966 - sum(depts.values()))
