def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(v1 - 25.0, 0)
    v3 = np.minimum(v1, v2)
    v4 = -(v3)
    return v4
