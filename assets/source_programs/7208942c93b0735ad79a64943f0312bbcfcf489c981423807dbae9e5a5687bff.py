def score(item, bins):
    delta = bins - item
    penalty = delta * delta - 15.0 * delta - 15.0
    score = -penalty * (bins + 1.0)
    return score
