def score(item, bins):
    return -np.maximum((bins - item) * np.maximum(bins - item - 10.0, 0.0) * ((bins - item) * np.maximum(bins - item - 10.0, 0.0)), 0.0)
