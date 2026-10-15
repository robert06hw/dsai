def score(item, bins):
    v1 = (bins - item)
    v2 = (v1 - 5.0)
    v3 = np.clip(v2, 0.0, 100.0)
    v4 = (v3 * v3)
    v5 = -(10000.0)
    v6 = np.clip(v4, v5, 0.0)
    return v6
