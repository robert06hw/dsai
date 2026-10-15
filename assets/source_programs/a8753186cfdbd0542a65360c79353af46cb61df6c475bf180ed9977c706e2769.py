def score(item, bins):
    residual = bins - item
    feasible_mask = residual > 5.0
    target_distance = residual - 5.0
    where_value = np.where(feasible_mask, target_distance, 0.0)
    product = residual * where_value
    negative_penalty = -(product ** 2)
    return negative_penalty
