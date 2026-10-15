def score(item, bins):
    return -np.minimum(bins - item, np.maximum(-25.0, bins - item))
