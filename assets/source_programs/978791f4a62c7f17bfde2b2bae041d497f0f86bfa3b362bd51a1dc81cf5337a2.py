import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.where(residual > 0, residual - 20.0, 0.0)
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = -np.where(product_3 > 0, product_3, 0.0)
    return negative_penalty_4
