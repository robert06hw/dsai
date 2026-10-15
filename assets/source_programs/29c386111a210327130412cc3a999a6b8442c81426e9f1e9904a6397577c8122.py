import numpy as np

def score(item, bins):
    feasible_mask_1 = np.where(bins - item >= 5.0, bins - item - 5.0, 0) > 0
    feasible_mask_2 = bins - item >= 5.0
    residual = bins - item
    target_distance_4 = residual - 5.0
    where_value_5 = np.where(feasible_mask_2, target_distance_4, 0)
    product_6 = where_value_5 * where_value_5
    where_value_7 = np.where(feasible_mask_1, product_6, 0)
    negative_penalty_8 = -where_value_7
    return negative_penalty_8
