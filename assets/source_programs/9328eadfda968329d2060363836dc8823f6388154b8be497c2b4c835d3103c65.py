def score(item, bins):
    x = bins - item
    return -np.minimum(x, np.maximum(x, -25.0))
