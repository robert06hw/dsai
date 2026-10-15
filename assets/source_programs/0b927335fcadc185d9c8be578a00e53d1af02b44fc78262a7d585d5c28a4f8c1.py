def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.minimum(v2, 5)
    v4 = np.clip(v3, 0, 1)
    v5 = np.maximum(v4, 0)
    v6 = -(v5)
    return v6
