import numpy as np

def score(item, bins):
    feasible_mask = bins >= item
    residual = bins - item
    where_value = np.where(feasible_mask, residual, 0.0)
    adjustment = where_value ** 2
    negative_penalty = -(adjustment)
    return negative_penalty
