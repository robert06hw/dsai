import numpy as np

def score(item, bins):
    feasible_mask_1 = bins >= item
    residual = (bins - item)
    where_value_3 = np.where(feasible_mask_1, residual, 0.0)
    adjustment_4 = np.square(where_value_3)
    negative_penalty_5 = -adjustment_4
    return negative_penalty_5
