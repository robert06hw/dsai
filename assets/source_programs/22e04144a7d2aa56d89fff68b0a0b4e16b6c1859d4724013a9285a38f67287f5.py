def score(item, bins):
    v1 = bins - item > 25.0
    v2 = bins - item
    v3 = np.where(v1, v2, 0)
    v4 = (v2 - 25.0)
    v5 = np.where(v1, v3, v4)
    v6 = np.where(v1, v5, 0)
    v7 = (v6 ** 3)
    v8 = -(v7)
    return v8
