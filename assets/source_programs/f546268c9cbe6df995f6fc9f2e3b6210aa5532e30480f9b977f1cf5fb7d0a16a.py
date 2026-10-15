def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = (bins - item)
    adjustment_3 = (residual ** 2)
    where_value_4 = np.where(feasible_mask_1, adjustment_3, 0)
    target_distance_5 = (where_value_4 - 25.0)
    where_value_6 = np.where(feasible_mask_1, target_distance_5, 0)
    sum_value_7 = np.sum(where_value_6)
    negative_penalty_8 = -(sum_value_7)
    product_9 = (negative_penalty_8 * where_value_4)
    return product_9
