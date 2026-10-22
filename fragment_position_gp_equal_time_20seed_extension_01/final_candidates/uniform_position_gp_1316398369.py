def score(item, bins):
    return np.maximum(bins - item, 12.0) / np.maximum(np.abs(bins), 1.0)
