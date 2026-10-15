def score(item, bins):
    return np.maximum(0.0, bins - item) ** 3 - 25.0 * np.maximum(0.0, bins - item) ** 2
