def score(item, bins):
    return -np.power(bins - item - 15.0, 3.0) + np.power(bins - item - 15.0 + 1.0, 2.0)
