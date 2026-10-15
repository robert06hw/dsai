def score(item, bins):
    residual = bins - item
    normalized_penalty = item / (residual + 1.0)
    return normalized_penalty
