def score(item, bins):
    v1 = (bins - item)
    v2 = np.maximum(v1 - 25.0, 0)
    v3 = np.minimum(v2, 0)
    v4 = np.maximum(v3, 0)
    v5 = np.minimum(v4, 0)
    v6 = -(v5)
    return v6
