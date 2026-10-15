def score(item, bins):
    return -((bins - item) ** 2 + 15.0 ** 2) * (bins + 1.0)
