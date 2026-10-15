import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.maximum(0, residual - 15.0)
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = -product_3
    adjustment_5 = target_distance_2 + 1.0
    product_6 = negative_penalty_4 * adjustment_5
    return product_6
