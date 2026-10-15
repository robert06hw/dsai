import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.maximum(residual - 5.0, 0)
    product_4 = target_distance_2 * target_distance_2
    negative_penalty_5 = -product_4
    return negative_penalty_5
