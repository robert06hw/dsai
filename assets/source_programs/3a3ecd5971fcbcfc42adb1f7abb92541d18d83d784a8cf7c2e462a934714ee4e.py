def score(item, bins):
    return np.maximum(-np.minimum(bins - item, bins - item), np.full_like(bins - item, -25.0))
