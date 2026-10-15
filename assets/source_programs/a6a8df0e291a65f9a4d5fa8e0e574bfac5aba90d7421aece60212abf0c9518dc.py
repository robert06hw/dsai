def score(item, bins):
    v1 = np.where(bins - item >= 5.0, bins - item - 5.0, 0.0)
    v2 = np.where(v1 >= 0.0, 1.0, 0.0)
    v3 = np.where(v1 >= 0.0, (bins - item), 0.0)
    v4 = np.where(v2 == 1.0, (v3 - 5.0), 0.0)
    v5 = np.where(v2 == 1.0, v4 * v4, 0.0)
    v6 = np.where(v1 >= 0.0, v5, 0.0)
    return v6
