def score(item, bins):
    return -bins + (np.where(bins >= item, bins - item, 0) * np.where(bins >= item, bins - item - 25, 0) - item)
