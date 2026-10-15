import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 5.0
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = -product_3
    score_array = np.where(residual >= 0, negative_penalty_4, 0.0)
    return score_array
