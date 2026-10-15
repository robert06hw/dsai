import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = bins - item
    target_distance_3 = residual - 5.0
    where_value_4 = np.where(feasible_mask_1, target_distance_3, 0.0)
    product_5 = where_value_4 * where_value_4
    negative_penalty_6 = -product_5
    return negative_penalty_6
