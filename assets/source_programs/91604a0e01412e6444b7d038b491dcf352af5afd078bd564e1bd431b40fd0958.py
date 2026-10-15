import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.where(residual >= 28, residual - 28, 0)
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = -product_3
    return negative_penalty_4
