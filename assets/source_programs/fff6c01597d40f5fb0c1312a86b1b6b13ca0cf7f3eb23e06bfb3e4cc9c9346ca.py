import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = bins - item
    target_distance_9 = residual ** 2 - 25.0
    where_value_10 = np.where(feasible_mask_1, target_distance_9, 0)
    sum_value_11 = np.sum(where_value_10)
    negative_penalty_12 = -sum_value_11
    product_13 = negative_penalty_12 * residual ** 2
    return product_13
