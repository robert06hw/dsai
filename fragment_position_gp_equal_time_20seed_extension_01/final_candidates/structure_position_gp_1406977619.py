def score(item, bins):
    return np.minimum(-np.maximum(np.abs(bins), 20.0 / (1.0 + 0.25)), bins)
