def score(item, bins):
    return -(bins - item) * (bins - item - 28.0) * (bins - item - 28.0)
