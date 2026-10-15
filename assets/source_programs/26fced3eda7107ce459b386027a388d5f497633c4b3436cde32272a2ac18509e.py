def score(item, bins):
    return np.where(bins >= item, bins - item, np.full_like(bins, -25.0))
