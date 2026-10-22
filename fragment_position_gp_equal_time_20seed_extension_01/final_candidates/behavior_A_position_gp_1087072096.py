def score(item, bins):
    return -((bins - item) * (np.maximum(bins - item, 0) - 25.0) * ((bins - item) * (np.maximum(bins - item, 0) - 25.0))) - item
