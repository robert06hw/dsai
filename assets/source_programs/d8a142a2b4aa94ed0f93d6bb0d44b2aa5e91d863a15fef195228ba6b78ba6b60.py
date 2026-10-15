def score(item, bins):
    return -np.square(bins - item) + 25.0
