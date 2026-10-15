def score(item, bins):
    return np.maximum(0, bins - item) + 0.3 * np.maximum(0, bins - item)
