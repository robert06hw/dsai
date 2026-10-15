def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = bins - item
    where_value_4 = np.where(feasible_mask_1, residual - 5.0, 0.0)
    product_5 = where_value_4 * where_value_4
    negative_penalty_6 = -(product_5)
    return negative_penalty_6
