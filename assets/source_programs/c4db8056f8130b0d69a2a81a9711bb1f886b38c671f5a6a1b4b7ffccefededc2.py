def score(item, bins):
    v1 = bins - item
    v2 = np.clip(v1, 0, 5)
    v3 = np.square(v2)
    v4 = -(v3)
    return v4
