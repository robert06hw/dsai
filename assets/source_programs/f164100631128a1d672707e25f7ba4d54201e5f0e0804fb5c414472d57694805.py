def score(item, bins):
    return np.where(bins >= item, (bins - item) * (bins - item) * 0.75 - item, np.inf)
