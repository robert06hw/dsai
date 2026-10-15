def score(item, bins):
    residual = bins - item
    negative_penalty = -((residual - 15.0)**2) * (bins + 1.0)
    return negative_penalty
