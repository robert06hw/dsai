def score(item, bins):
    scores = -(((bins - item) * ((bins - item) - 25.0)) * ((bins - item) * ((bins - item) - 25.0)))
    return scores
