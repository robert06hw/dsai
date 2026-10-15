def score(item, bins):
    return -np.sqrt(np.sum((bins - item) ** 2)) / bins + 0.2 * (bins - item)
