def score(item, bins):
    return -np.clip(bins - item, 0, 10.0)
