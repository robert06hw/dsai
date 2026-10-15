import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = (bins - item)
    where_value_3 = np.where(feasible_mask_1, residual, 0.0)
    product_4 = where_value_3 * where_value_3
    negative_penalty_5 = np.where(product_4 > 0, -product_4, 0.0)
    return negative_penalty_5
