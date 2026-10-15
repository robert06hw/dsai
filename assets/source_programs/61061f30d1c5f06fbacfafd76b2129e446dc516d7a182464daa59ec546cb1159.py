def score(item, bins):
    return -np.maximum(0, (bins - item)) ** 2
