import numpy as np

def score(item, bins):
    residual = (bins - item)
    feasible_mask = bins - item > 5.0
    target_distance = (residual - 5.0)
    where_value = np.where(feasible_mask, target_distance, 0.0)
    product = (residual * where_value)
    product_squared = (product * product)
    negative_penalty = -(product_squared)
    return negative_penalty
