def score(item, bins):
    capacity = 100.0
    v1 = bins >= item + 5.0
    v2 = bins >= item
    v3 = capacity - bins
    v4 = v3 - item
    v5 = np.where(v1, v4, 0.0)
    v6 = v5 * v5
    v7 = np.where(v2, v6, 0.0)
    v8 = np.where(v1, v7, 0.0)
    v9 = -(v8)
    return v9
