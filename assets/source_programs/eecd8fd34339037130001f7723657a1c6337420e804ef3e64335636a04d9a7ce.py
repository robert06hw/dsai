import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item >= 0
    residual = (bins - item)
    target_distance_3 = (residual - 5.0)
    product_4 = (target_distance_3 * target_distance_3)
    negative_penalty_5 = -(product_4)
    where_value_6 = np.where(feasible_mask_1, negative_penalty_5, 0.0)
    return where_value_6
