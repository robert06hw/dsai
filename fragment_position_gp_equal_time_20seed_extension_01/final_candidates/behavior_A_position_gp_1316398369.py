def score(item, bins):
    return np.sqrt(np.square(bins - item - 15.0)) / bins
