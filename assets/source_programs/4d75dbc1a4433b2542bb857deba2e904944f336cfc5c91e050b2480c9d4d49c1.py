def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = (bins - item)
    where_value_3 = np.where(feasible_mask_1, residual, 0.0)
    normalized_penalty_4 = (where_value_3 / 100.0)
    adjustment_5 = (normalized_penalty_4 ** 2)
    negative_penalty_6 = -(adjustment_5)
    sorted_indices = np.argsort(negative_penalty_6)[::-1]
    return negative_penalty_6[sorted_indices][:bins.shape[0]]
