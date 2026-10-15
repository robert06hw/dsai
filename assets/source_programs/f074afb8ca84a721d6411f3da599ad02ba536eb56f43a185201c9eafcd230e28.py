def score(item, bins):
    v1 = bins - item
    v2 = np.square(v1)
    v3 = np.maximum(v2, 0)
    v4 = np.sqrt(v3)
    return v4
