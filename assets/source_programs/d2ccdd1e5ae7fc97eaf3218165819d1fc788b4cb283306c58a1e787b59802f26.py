def score(item, bins):
    return -(((bins - item) - (20.0 / (item + 1.0))) * ((bins - item) - (20.0 / (item + 1.0))))
