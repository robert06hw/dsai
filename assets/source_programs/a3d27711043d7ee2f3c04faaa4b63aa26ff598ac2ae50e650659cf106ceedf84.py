def score(item, bins):
    v1 = np.maximum(bins - item, 0)
    v2 = v1 ** 3
    v3 = -v2
    return v3
