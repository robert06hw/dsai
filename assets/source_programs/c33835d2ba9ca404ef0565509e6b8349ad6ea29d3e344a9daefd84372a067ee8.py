def score(item, bins):
    v1 = bins - item
    v2 = v1 - 5.0
    v3 = v2 * v2
    v4 = -np.maximum(v3, 0.0)
    return v4
