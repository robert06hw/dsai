def score(item, bins):
    return -(((bins - item) - 0.25 * item) ** 2)
