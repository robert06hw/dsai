def score(item, bins):
    return -((bins - item) ** 2 - 25.0) * np.maximum(bins - item, 0)
