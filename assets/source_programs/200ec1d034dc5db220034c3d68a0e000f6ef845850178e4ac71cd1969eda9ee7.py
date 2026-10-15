def score(item, bins):
    residual = bins - item
    feasible_mask = residual > 0
    target_distance = residual
    where_value = np.where(feasible_mask, target_distance, 0.0)
    product = where_value * where_value
    negative_penalty = -product
    return negative_penalty
