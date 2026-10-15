def score(item, bins):
    return np.maximum(-(np.maximum(bins - item, 0) * np.log(bins - item + 1e-10)) + 25.0, 0)
