def score(item, bins):
    return -(np.clip(bins - item, 0, 5) * np.clip(np.clip(-(bins - 24 - item), 0, 5), 0, 10.0))
