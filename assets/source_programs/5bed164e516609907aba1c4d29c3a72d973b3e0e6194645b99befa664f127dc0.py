def score(item, bins):
    v1 = bins - item
    v2 = np.maximum(0, v1 - 5.0)
    v3 = v2 * v2
    return -(v3)
