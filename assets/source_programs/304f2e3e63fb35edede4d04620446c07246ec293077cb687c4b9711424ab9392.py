import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.where(residual >= 25.0, residual - 25.0, 0)
    adjustment_3 = np.power(target_distance_2, 3)
    negative_penalty_4 = -np.multiply(adjustment_3, residual < 25.0)
    return negative_penalty_4
