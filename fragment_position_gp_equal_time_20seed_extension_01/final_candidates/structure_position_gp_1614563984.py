def score(item, bins):
    return np.square(np.abs(bins - item - 12.0))
