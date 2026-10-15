def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = bins + 1.0
    v4 = v2 / v3
    v5 = -(v4)
    v6 = 0.2 * v1
    v7 = v5 + v6
    return v7
