def score(item, bins):
    v1 = bins - item
    v2 = v1 - 25.0
    v3 = np.maximum(v2, 0)
    v4 = v1 * v3
    v5 = np.where(v4 > 0, v4 * v4, 0)
    v6 = -(v5)
    return v6
