def score(item, bins):
    return -np.clip((bins - item) * np.clip(bins - item, 0, item), 0, np.abs(-100.0))
