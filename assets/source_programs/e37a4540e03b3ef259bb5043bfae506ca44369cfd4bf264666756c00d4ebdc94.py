import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = np.where(residual > 0, residual + 1.0, 1.0)
    normalized_penalty_3 = item / adjustment_2
    target_distance_4 = residual - normalized_penalty_3
    product_5 = target_distance_4 * target_distance_4
    negative_penalty_6 = -product_5
    return negative_penalty_6
