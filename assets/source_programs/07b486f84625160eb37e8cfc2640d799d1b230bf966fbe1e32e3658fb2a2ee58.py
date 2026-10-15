import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment = residual ** 2
    adjustment_squared = adjustment ** 2
    target_distance = adjustment_squared - 25.0
    sum_value = np.sum(target_distance)
    negative_penalty = -sum_value
    product = negative_penalty * adjustment
    return product
