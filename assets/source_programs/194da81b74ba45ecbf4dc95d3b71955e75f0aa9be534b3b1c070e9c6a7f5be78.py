import numpy as np

def score(item, bins):
    feasible_mask_1 = bins >= item
    residual = np.where(feasible_mask_1, bins - item, 0.0)
    adjustment_4 = np.square(residual)
    negative_penalty_5 = np.multiply(adjustment_4, -1.0)
    return negative_penalty_5
