import numpy as np

def score(item, bins):
    feasible_mask = bins - item >= 5.0
    residual = bins - item
    target_distance = residual - 5.0
    where_value = np.where(feasible_mask, target_distance, 0)
    product = where_value * where_value
    negative_penalty = -np.where(feasible_mask, product, 0)
    return negative_penalty
