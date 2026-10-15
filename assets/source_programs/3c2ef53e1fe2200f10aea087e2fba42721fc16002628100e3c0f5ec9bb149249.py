import numpy as np

def score(item, bins):
    feasible_mask = bins - item > 0
    residual = bins - item
    where_value = np.where(feasible_mask, residual, 0.0)
    product = where_value * where_value
    penalty = -(product)
    return penalty
