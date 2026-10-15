def score(item, bins):
    v1 = bins - item >= 5.0
    v2 = bins - item >= 0.0
    v3 = np.maximum(v1, v2)
    v4 = np.power(v3, 2)
    v5 = -v4
    return v5
