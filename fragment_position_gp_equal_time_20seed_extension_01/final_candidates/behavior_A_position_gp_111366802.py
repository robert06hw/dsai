def score(item, bins):
    return -(bins - item) / np.maximum(np.abs(np.maximum(bins - item - 20.0, 0.0) * np.maximum(bins - item - 20.0, 0.0)), 0.75)
