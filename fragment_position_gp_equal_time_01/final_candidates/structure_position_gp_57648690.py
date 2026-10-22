def score(item, bins):
    return -np.square(np.clip(bins - item, 0, 5))
