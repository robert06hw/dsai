def score(item, bins):
    return -np.where(bins - item > 25.0, bins - item, 0) ** 3
