import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.maximum(residual - 5.0, 0)
    negative_penalty_3 = -target_distance_2
    product_4 = negative_penalty_3 * target_distance_2
    return product_4
