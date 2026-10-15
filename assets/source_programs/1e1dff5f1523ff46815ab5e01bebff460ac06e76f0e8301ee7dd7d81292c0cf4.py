def score(item, bins):
    return (-((bins - item) * (bins - item)) / (bins + 1.0)) + (0.45 * (bins - item))
