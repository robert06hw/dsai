def score(item, bins):
    residual = bins - item
    penalty = residual / (residual + 1.0)
    return -penalty
