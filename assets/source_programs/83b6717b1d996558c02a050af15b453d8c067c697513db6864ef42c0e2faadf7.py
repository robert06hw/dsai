def score(item, bins):
    v1 = (bins - item) > 0
    v2 = (bins - item) - 5.0
    v3 = np.maximum(v2, 0)
    v4 = v3 ** 2
    v5 = -(v4)
    return np.where(v1, v5, 0)
