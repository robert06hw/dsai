def score(item, bins):
    return np.minimum(-np.maximum(bins, 20.0 / (1.0 + 0.25)), bins)
