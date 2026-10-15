def score(item, bins):
    return -(((bins - item) - (1.25 * item)) * ((bins - item) - (1.25 * item)))
