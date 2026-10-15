def score(item, bins):
    return -((bins - item) * (bins - item)) + 25.0 * np.sum(bins >= item)
