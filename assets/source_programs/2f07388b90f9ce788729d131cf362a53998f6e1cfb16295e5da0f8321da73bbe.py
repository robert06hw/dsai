def score(item, bins):
    return -np.where(bins >= item, bins - item, 0) ** 3
