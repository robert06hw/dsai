import numpy as np

def score(item, bins):
    feasible_mask_1 = bins >= item
    residual = np.where(feasible_mask_1, bins - item, 0)
    power_value_4 = np.power(residual, 3)
    negative_penalty_5 = -power_value_4
    return negative_penalty_5
