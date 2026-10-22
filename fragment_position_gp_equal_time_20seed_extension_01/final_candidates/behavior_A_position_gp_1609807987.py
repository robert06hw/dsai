def score(item, bins):
    return np.square((np.clip(bins - item, 0, 40.0) - 20.0) ** 2)
