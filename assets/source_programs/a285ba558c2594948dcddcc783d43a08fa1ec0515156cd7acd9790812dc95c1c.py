def score(item, bins):
    v1 = np.logical_and(bins >= item, bins <= 25)
    v2 = bins - item
    v3 = np.where(v1, v2, 0)
    v4 = v3 * 25
    v5 = v4 * v4
    v6 = -v5
    v7 = np.where(v1, v6, 0)
    return v7
