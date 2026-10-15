def score(item, bins):
    return -1.0 * (bins - item) ** 2 * (bins + 1.0)
