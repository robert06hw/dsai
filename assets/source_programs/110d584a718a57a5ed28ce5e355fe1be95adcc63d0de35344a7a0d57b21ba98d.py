def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    v3 = np.maximum(v1, 0) + np.maximum(v2, 0)
    return v3
