import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = residual ** 2
    adjustment_3 = adjustment_2 ** 2
    target_distance_4 = adjustment_3 - 25.0
    negative_penalty_6 = -np.sum(target_distance_4)
    product_7 = negative_penalty_6 * adjustment_2
    return product_7
