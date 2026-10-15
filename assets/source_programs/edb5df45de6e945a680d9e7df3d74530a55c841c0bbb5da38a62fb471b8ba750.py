def score(item, bins):
    return np.where(item <= bins, -(((bins - item) * (bins - item)) / (bins + 1.0)) + (0.45 * (bins - item)), 0)
