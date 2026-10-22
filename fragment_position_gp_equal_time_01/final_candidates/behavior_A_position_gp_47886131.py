def score(item, bins):
    return -(np.clip(bins - item, 0, 5) * np.clip(bins - item, 0, 5) - 2)
