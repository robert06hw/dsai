def score(item, bins):
    v1 = bins - item
    v2 = v1 - 5.0
    v3 = v2 * v2
    v4 = -(v3)
    return np.where(v4 > 0, 0, v4)
