def score(item, bins):
    capacity = 100.0
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = v2 * v2
    v4 = -(v3 * v2)
    return v4
