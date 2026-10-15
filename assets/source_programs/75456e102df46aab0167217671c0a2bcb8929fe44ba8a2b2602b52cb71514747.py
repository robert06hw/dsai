def score(item, bins):
    feasible_mask = bins >= item
    residual = (bins - item) * feasible_mask
    power_value = residual ** 3
    negative_penalty = -power_value
    return negative_penalty
