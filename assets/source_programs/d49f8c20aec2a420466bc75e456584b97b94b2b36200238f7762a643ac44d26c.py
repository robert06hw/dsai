def score(item, bins):
    return 100 - np.clip(bins - item, 0, 100)
