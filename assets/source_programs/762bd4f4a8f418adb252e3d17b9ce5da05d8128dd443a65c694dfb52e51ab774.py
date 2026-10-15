def score(item, bins):
    score = -(((bins - item) - 28.0) * ((bins - item) - 28.0))
    return score
