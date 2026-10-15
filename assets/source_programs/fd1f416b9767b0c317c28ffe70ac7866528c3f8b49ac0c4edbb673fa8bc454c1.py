import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 28.0
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = np.minimum(product_3, 0.0)
    return negative_penalty_4
