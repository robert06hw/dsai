def score(item, bins):
    return np.where(bins - item > 75.0, np.where(bins - item > 50.0, np.where(bins - item > 25.0, bins - item, 0), bins - item - 25.0), 0) ** 3
