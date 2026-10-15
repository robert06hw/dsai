def score(item, bins):
    return -np.power(bins - item - 28.0, 2)
