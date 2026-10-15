def score(item, bins):
    return np.maximum(0, bins - item) ** 2 / (bins + 1) + 0.45 * (bins - item)
