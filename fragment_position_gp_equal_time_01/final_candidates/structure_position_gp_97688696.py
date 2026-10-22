def score(item, bins):
    return np.where((bins - item) * (np.maximum(bins - item, 0) - 25.0) * ((bins - item) * (np.maximum(bins - item, 0) - 25.0)) > item, bins - item, 100.0)
