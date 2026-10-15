def score(item, bins):
    return np.where(item - bins >= 0, 0, ((bins - item) - 20.0) * ((bins - item) - 20.0))
