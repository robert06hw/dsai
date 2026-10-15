def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.maximum(v2 - 5.0, 0)
    v4 = np.maximum(v3 - 5.0, 0)
    v5 = np.maximum(v4 - 5.0, 0)
    v6 = -(v5 * v5)
    return v6
