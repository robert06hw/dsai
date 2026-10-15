def score(item, bins):
    return -np.minimum(bins - item, 0) * np.minimum(bins - item, 0)
