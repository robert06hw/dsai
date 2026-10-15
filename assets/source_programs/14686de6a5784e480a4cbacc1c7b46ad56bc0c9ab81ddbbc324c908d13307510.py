def score(item, bins):
    v1 = np.maximum(np.maximum(bins - item, 0) - 5.0, 0) ** 2 == 0
    v2 = bins - item
    v3 = np.maximum(v2, 0)
    v4 = v3 - 5.0
    v5 = np.maximum(v4, 0)
    v6 = v5 ** 2
    v7 = -v6
    v8 = np.where(v1, 0, v7)
    return v8
