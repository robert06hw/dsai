import numpy as np

def score(item, bins):
    feasible_mask = bins >= item
    residual = bins - item
    where_value = np.where(feasible_mask, residual, 0.0)
    product = where_value * where_value
    negative_penalty = -product
    max_index = np.argmax(negative_penalty)
    return np.zeros_like(bins)
