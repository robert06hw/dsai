def score(item, bins):
    v1 = (bins - item)
    v2 = np.where(v1 > 0, v1, 12.0)
    v3 = v2 * v2
    return -v3
