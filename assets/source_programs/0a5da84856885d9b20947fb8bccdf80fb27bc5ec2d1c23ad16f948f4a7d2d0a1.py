def score(item, bins):
    return np.maximum(bins - item, 0) * (bins - item - 15.0) ** 2 * -(bins + 1.0)
