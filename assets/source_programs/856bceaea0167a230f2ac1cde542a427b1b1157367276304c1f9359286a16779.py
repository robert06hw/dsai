def score(item, bins):
    v1 = bins >= item + 5.0
    v2 = bins >= item
    v3 = (bins - item)
    v4 = (v3 - 5.0)
    v5 = np.where(v1, v4, 0.0)
    v6 = np.where(v2, v5, 0.0)
    v8 = np.where(v1, v6, 0.0)
    v9 = -(v8)
    return v9
