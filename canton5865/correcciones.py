"""Correcciones a la transcripción de Cantón, verificadas contra la imagen de la página
(scratch/canton_pages/p_<pdf>.png). Cada entrada: (año, cargo, provincia, categoría,
unidad, columna, valor_transcripto, valor_corregido, motivo)."""
C = [
    # --- Capital 1958: correcciones manuscritas en el ejemplar (tinta roja) ---
    (1958, 'P', 'Capital Federal', 'M', 'Balvanera Oeste', 1, 24922, 27134, 'p252: corrección manuscrita (impreso 24.922)'),
    (1958, 'P', 'Capital Federal', 'M', 'Balvanera Oeste', 2, 15053, 24922, 'p252: corrección manuscrita (impreso 15.053); cierra con la suma de partidos'),
    (1958, 'P', 'Capital Federal', 'M', 'Balvanera Sud', 1, 27134, 15053, 'p252: corrección manuscrita (impreso 27.134); 13.498 + 15.053 = 28.551 del total corregido'),
    (1958, 'P', 'Capital Federal', 'M', 'San Cristóbal Norte', 1, 32244, 22244, 'p252: dígito corregido a mano sobre el 3; 20.244 (lectura de la transcripción) daría más votantes que inscriptos'),
    (1958, 'P', 'Capital Federal', 'T', 'Balvanera Oeste', 1, 47518, 51734, 'p254: corrección manuscrita'),
    (1958, 'P', 'Capital Federal', 'T', 'Balvanera Oeste', 2, 39653, 47518, 'p254: corrección manuscrita'),
    (1958, 'P', 'Capital Federal', 'T', 'Balvanera Sud', 1, 40632, 28551, 'p254: corrección manuscrita'),
    (1958, 'P', 'Capital Federal', 'T', 'San Cristóbal Norte', 1, 53128, 43128, 'consecuencia de la corrección de mujeres (20.884 + 22.244)'),
    # --- 1958: celdas que fijan a la vez la suma de la fila y V+M=T (un solo valor posible) ---
    (1958, 'D', 'Corrientes', 'M', 'San Martín', 11, 1106, 1100, 'p291: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'V', 'Almirante Brown', 7, 69, 169, 'p256: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'M', 'Balcarce', 10, 33, 23, 'p264: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'M', 'Carmen de Areco', 3, 1, 4, 'p264: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'V', 'Coronel Pringles', 3, 19, 29, 'p256: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'T', 'Esteban Echeverría', 3, 44, 88, 'p272: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'V', 'La Plata', 17, 4158, 4156, 'p259: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'V', 'Leandro N. Alem', 12, 59, 58, 'p259: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'T', 'Rivadavia', 2, 6613, 6163, 'p276: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'T', 'Tapalqué', 11, 9, 4, 'p278: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Buenos Aires', 'V', 'Tres Arroyos', 17, 1683, 1083, 'p263: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Capital Federal', 'M', 'Flores', 17, 118, 198, 'p253: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Capital Federal', 'M', 'Pilar', 7, 3234, 3243, 'p252: cierra la suma de la fila y varones+mujeres=total; el libro imprime 3.234 (errata)'),
    (1958, 'P', 'Capital Federal', 'M', 'San Juan Evangelista', 4, 39, 89, 'p252: cierra la suma de la fila y varones+mujeres=total; el libro imprime 39 (errata)'),
    (1958, 'P', 'Capital Federal', 'T', 'Vélez Sarsfield', 16, 16780, 16870, 'p255: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Chubut', 'M', 'Rawson', 10, 540, 640, 'p300: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'V', 'Colón', 11, 4784, 5265, 'p283: cierra la suma de la fila y varones+mujeres=total; columna 11 tapada por el pliegue: la transcripción leyó mal'),
    (1958, 'P', 'Córdoba', 'T', 'Cruz del Eje', 3, 10, 110, 'p287: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'V', 'Cruz del Eje', 11, 4764, 4784, 'p283: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'V', 'General Roca', 11, 2341, 2342, 'p283: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'T', 'Ischillín', 11, 5274, 5174, 'p287: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'V', 'Juárez Celman', 11, 3897, 3697, 'p283: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'M', 'Río Cuarto', 7, 368, 308, 'p285: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'V', 'Río Segundo', 11, 5815, 5813, 'p283: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'T', 'San Alberto', 12, 2957, 2958, 'p288: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Córdoba', 'V', 'Tercero Arriba', 12, 8525, 8545, 'p284: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Entre Ríos', 'V', 'Nogoyá', 4, 301, 361, 'p304: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Mendoza', 'V', 'Rivadavia', 7, 29, 28, 'p322: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Mendoza', 'V', 'Tunuyán', 2, 4416, 4446, 'p322: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Neuquén', 'V', 'Collón-Curá', 8, 45, 46, 'p334: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Neuquén', 'M', 'Chos-Malal', 8, 142, 143, 'p335: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Neuquén', 'V', 'Ñorquín', 7, 19, 9, 'p334: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Neuquén', 'V', 'Zapala', 5, 55, 65, 'p334: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Salta', 'V', 'Capital', 4, 545, 546, 'p337: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Salta', 'M', 'General Martín Miguel de Güemes', 14, 321, 311, 'p340: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Santa Fe', 'V', 'La Capital', 2, 66468, 66469, 'p357: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Santa Fe', 'V', 'San Javier', 13, 83, 183, 'p358: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Santa Fe', 'V', 'Vera', 8, 10, 0, 'p357: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Santiago del Estero', 'V', 'Belgrano', 9, 51, 519, 'p363: cierra la suma de la fila y varones+mujeres=total; el libro imprime 51 (errata o cifra perdida)'),
    (1958, 'P', 'Santiago del Estero', 'M', 'Pellegrini', 2, 2480, 2380, 'p365: cierra la suma de la fila y varones+mujeres=total'),
    (1958, 'P', 'Tucumán', 'V', 'Trancas', 13, 328, 338, 'p370: cierra la suma de la fila y varones+mujeres=total'),
    # --- 1958: casos ambiguos resueltos combinando los controles ---
    (1958, 'P', 'Chubut', 'M', 'Rawson', 1, 491, 3491, 'p300: 491 inscriptas con 3.063 votantes es imposible; V+M=T da 3.491'),
    (1958, 'P', 'Córdoba', 'M', 'San Alberto', 11, 1578, 1698, 'p285: con V corregido cierran la fila de mujeres y V+M=T'),
    (1958, 'P', 'Córdoba', 'V', 'San Alberto', 11, 1925, 1929, 'p283: idem (columna tapada por el pliegue)'),
    (1958, 'P', 'Formosa', 'T', 'Pilcomayo', 7, 1208, 1808, 'p312: V+M=T en las dos columnas y la fila cierra'),
    (1958, 'P', 'Formosa', 'T', 'Pilcomayo', 8, 2607, 2067, 'p312: idem'),
    (1958, 'P', 'Mendoza', 'V', 'San Carlos', 2, 3011, 3044, 'p322: las tres correcciones de varones cierran la fila y V+M=T'),
    (1958, 'P', 'Mendoza', 'V', 'San Carlos', 3, 7, 4, 'p322: idem'),
    (1958, 'P', 'Mendoza', 'V', 'San Carlos', 10, 1225, 1215, 'p322: idem'),
    (1958, 'D', 'Corrientes', 'V', 'San Miguel', 1, 1482, 1982, 'p289: 1.482 inscriptos con 1.760 votantes es imposible; V+M=T da 1.982'),
    # --- 1962 y 1965: lectura de la imagen (solo hay tabla de totales; se corrige si la cifra
    #     releída es compatible con la imagen y hace cerrar la fila) ---
    (1962, 'D', 'Corrientes', 'T', 'Saladas', 6, 70, 170, 'p389: corrección manuscrita «170» sobre el 70 impreso; cierra la fila'),
    (1965, 'D', 'Corrientes', 'T', 'Bella Vista', 10, 1508, 1908, 'p428: el libro dice 1.908; cierra la fila'),
    (1965, 'D', 'Corrientes', 'T', 'Goya', 9, 1319, 2319, 'p428: el libro dice 2.319; cierra la fila'),
    (1965, 'D', 'Capital Federal', 'T', 'Pilar', 18, 10400, 18400, 'p411 (escaneo desvaído): se lee 18.400; con la col. 14 cierra la fila'),
    (1965, 'D', 'Capital Federal', 'T', 'Pilar', 14, 2229, 2239, 'p411: dígito ilegible; el valor que cierra la fila es compatible con la imagen'),
    (1965, 'D', 'Capital Federal', 'T', 'Belgrano', 12, 8377, 6377, 'p411: el libro dice 6.377'),
    (1965, 'D', 'Capital Federal', 'T', 'Belgrano', 13, 3530, 6990, 'p411: se lee «6.?90»; 6.990 cierra la fila'),
    (1965, 'D', 'Capital Federal', 'T', 'San Cristóbal Sud', 18, 17706, 19706, 'p411: se lee «1?.706»; 19.706 cierra la fila junto con la col. 17'),
    (1965, 'D', 'Capital Federal', 'T', 'San Cristóbal Sud', 17, 1292, 1222, 'p411: se lee «1.2?2»'),
    (1965, 'D', 'Capital Federal', 'T', 'San Nicolás', 12, 1450, 1990, 'p411: se lee «1.??0»; 1.990 cierra la fila con las cols. 13 y 18'),
    (1965, 'D', 'Capital Federal', 'T', 'San Nicolás', 13, 1378, 1376, 'p411: el libro dice 1.376'),
    (1965, 'D', 'Capital Federal', 'T', 'San Nicolás', 18, 12055, 12095, 'p411: el libro dice 12.095'),
    (1965, 'D', 'Capital Federal', 'T', 'San Carlos Sud', 14, 2514, 2914, 'p411: se lee «2.?14»; 2.914 cierra la fila'),
    (1965, 'D', 'Capital Federal', 'T', 'Palermo', 13, 2846, 2646, 'p411: el libro dice 2.646'),
    (1965, 'D', 'Capital Federal', 'T', 'Palermo', 17, 3230, 3330, 'p411: se lee «3.?30»; 3.330 cierra la fila'),
    (1965, 'D', 'Capital Federal', 'T', 'San Cristóbal Norte', 17, 1242, 1222, 'p411: se lee «1.2?2»; 1.222 cierra la fila'),
    # --- cotejo con la tabla provincial de Wikipedia: la celda que hace cerrar la fila y también el total provincial ---
    (1962, 'D', 'Santa Fe', 'T', 'Belgrano', 15, 2743, 1743, 'p406: la fila excede a los votantes en 1.000 y el total provincial de la UCRP excede al de Wikipedia en 1.000'),
    (1965, 'D', 'Mendoza', 'T', 'Rivadavia', 3, 4807, 4087, 'p440: el libro dice 4.807; la fila excede a los votantes en 720 y el Partido Demócrata provincial supera a Wikipedia en 720'),
    (1965, 'D', 'Mendoza', 'T', 'Tupungato', 11, 365, 865, 'p441: la fila queda 500 debajo de los votantes y la Unión Popular provincial 497 debajo de Wikipedia'),
    # --- 1965, provincias sin tabla de Wikipedia: la celda que hace cerrar la fila y el total provincial del tomo I (p. 239-246 impresas) ---
    (1965, 'D', 'La Rioja', 'T', 'Capital', 10, 5479, 5429, 'p438: el libro imprime 5.479 (errata); la fila queda 50 por encima de los votantes y la Unión Popular provincial 50 por encima del tomo I'),
    (1965, 'D', 'Misiones', 'T', 'Capital', 10, 597, 697, 'p442: primer dígito borroso; 697 cierra la fila y el total provincial del tomo I'),
    (1965, 'D', 'Misiones', 'T', 'Guaraní', 11, 21, 11, 'p442: el libro dice 11; cierra la fila y el total provincial del tomo I'),
]

def aplicar(T, log=None):
    for a, c, p, cat, u, k, old, new, why in C:
        r = T[(a, c, p, cat)]['rows'][u]
        if r.get(k) != old:
            raise ValueError(f'{a} {p} {cat} {u} col{k}: se esperaba {old}, hay {r.get(k)}')
        r[k] = new
        if log is not None: log.append((a, c, p, cat, u, k, old, new, why))

# Celdas que faltan en la página (no son correcciones): se imputa el residuo contra la tabla
# provincial de Wikipedia solo cuando el resto de la provincia cierra. Van marcadas en la ficha.
IMPUTA = [
    (1962, 'D', 'Buenos Aires', 'T', 'Florencio Varela', k, v,
     'p379 cortada al pie: falta la mitad izquierda de la fila; residuo del total provincial de Wikipedia')
    for k, v in ((3, 2361), (4, 3656), (5, 190), (6, 171), (7, 394), (8, 177), (9, 223), (10, 85), (11, 135))
]

def imputar(T, log=None):
    for a, c, p, cat, u, k, v, why in IMPUTA:
        r = T[(a, c, p, cat)]['rows'][u]
        if isinstance(r.get(k), int):
            raise ValueError(f'{a} {p} {u} col{k}: ya tiene valor {r[k]}')
        r[k] = v
        T[(a, c, p, cat)].setdefault('imput', set()).add(u)
        if log is not None: log.append((a, c, p, cat, u, k, None, v, why))
