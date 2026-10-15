def score(item, bins):
    residual = bins - item
    adjustment = item + 1.0
    normalized_penalty = 20.0 / adjustment
    target_distance = residual - normalized_penalty
    product = target_distance * target_distance
    negative_penalty = -product
    return negative_penalty
