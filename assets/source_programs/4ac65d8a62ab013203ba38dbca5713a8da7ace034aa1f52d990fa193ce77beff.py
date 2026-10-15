import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.maximum(0, residual - 5.0)
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = -product_3
    return negative_penalty_4
