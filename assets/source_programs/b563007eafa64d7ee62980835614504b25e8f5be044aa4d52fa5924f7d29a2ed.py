def score(item, bins):
    v1 = bins - item
    v2 = np.where(v1 >= 0, 12.0, 0.0)
    v3 = np.where(v1 > 0, v1 - v2, 0.0)
    v4 = np.where(v3 > 0, v3**2, 0.0)
    return -v4
