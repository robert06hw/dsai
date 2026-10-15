def score(item, bins):
    return -((bins - item) * (bins - item - 28.0)) ** 2
