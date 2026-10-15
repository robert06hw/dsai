def score(item, bins):
    return np.maximum(0, np.log((bins - item) + 1) - 0.45 * item) / bins
