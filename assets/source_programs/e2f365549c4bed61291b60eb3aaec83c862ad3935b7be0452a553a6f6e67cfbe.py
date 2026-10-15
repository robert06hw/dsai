def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1, 0)
    v3 = np.maximum(v1 + 1e-10, 0)
    v4 = np.log(v3)
    v5 = v2 * v4
    v6 = -(v5)
    v7 = (v6 + 25.0)
    v8 = np.maximum(v7, 0)
    return v8
