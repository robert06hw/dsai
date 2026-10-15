def score(item, bins):
    return np.minimum(100 - bins, 0)
