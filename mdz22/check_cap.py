# Let's count mesas per department from our visual inspection:
# Page 325 (Capital part 1):
cap_1 = [
    (1, 5), (2, 9), (3, 8), (4, 7), (5, 8), (6, 4), (8, 12), (10, 6),
    (12, 2), (13, 5), (14, 5), (16, 4), (17, 3), (18, 1), (22, 8), (23, 1),
    (24, 5), (25, 3), (26, 19), (27, 4), (28, 11), (29, 1), (30, 1), (31, 4),
    (37, 5), (39, 4), (40, 6), (41, 3), (42, 5), (43, 6), (45, 13), (46, 2),
    (47, 3), (50, 5)
]

# Page 327 (Capital part 2):
cap_2 = [
    (51, 4), (52, 8), (54, 4), (55, 3), (56, 4), (57, 3), (58, 2),
    (60, 3), (68, 3), (71, 3), (33, 1)
]

print("Capital mesas count:", len(cap_1) + len(cap_2))
print("Capital votantes sum:", sum(v for m, v in cap_1) + sum(v for m, v in cap_2))
