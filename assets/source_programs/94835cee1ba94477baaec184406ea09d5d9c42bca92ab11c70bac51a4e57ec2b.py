def score(item, bins):
    return np.maximum(0, np.minimum(bins - item, 12.0) * (bins - item) * (bins - item))
