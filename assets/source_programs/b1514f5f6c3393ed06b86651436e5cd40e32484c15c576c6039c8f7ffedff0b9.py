import numpy as np

def score(item, bins):
    feasible_mask_1 = bins >= item
    where_value_3 = np.where(feasible_mask_1, bins - item, 0.0)
    adjustment_4 = (where_value_3 ** 2)
    negative_penalty_5 = -(adjustment_4)
    return negative_penalty_5
