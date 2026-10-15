def score(item, bins):
    v1 = bins - item
    v2 = v1 - 5.0
    v3 = np.multiply(v1, v2)
    v4 = -v3
    return v4
