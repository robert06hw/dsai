def score(item, bins):
    feasible_mask_1 = bins - item > 25.0
    residual = np.clip(bins - item, 0, 100)
    where_value_3 = np.where(feasible_mask_1, residual, 0)
    adjustment_4 = where_value_3 ** 3
    negative_penalty_5 = -(adjustment_4)
    return negative_penalty_5
