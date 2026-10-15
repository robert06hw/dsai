def score(item, bins):
    v1 = bins - item
    v2 = np.where(v1 > 0, v1, 18.0)
    v3 = v2 * v2
    v4 = -(v3)
    v5 = bins + 1.0
    v6 = v4 / v5
    return v6
