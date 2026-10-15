import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.where(residual > 0, residual - 25.0, 0)
    product_3 = residual * target_distance_2
    product_4 = product_3 * product_3
    negative_penalty_5 = -np.where(residual > 0, product_4, 0)
    return negative_penalty_5
