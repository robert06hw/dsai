import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item >= 0.0
    residual = bins - item
    product_3 = residual * feasible_mask_1
    product_4 = product_3 * product_3
    negative_penalty_5 = -product_4
    where_value_6 = np.where(feasible_mask_1, negative_penalty_5, 0.0)
    return where_value_6
