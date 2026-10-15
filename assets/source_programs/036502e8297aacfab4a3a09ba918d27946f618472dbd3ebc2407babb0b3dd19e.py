def score(item, bins):
    return -(((bins - item) - 15.0) * ((bins - item) - 15.0))
