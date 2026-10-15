import numpy as np

def score(item, bins):
    feasible_mask = bins >= item
    residual = bins - item
    where_value = np.where(feasible_mask, residual, 0)
    power_value = np.power(where_value, 2)
    negative_penalty = -power_value
    return negative_penalty
