def score(item, bins):
    return bins - item + 15.0 - ((bins - item - 15.0) ** 2) - ((bins - item - 15.0) + 1.0)
