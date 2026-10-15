import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 25.0
    minimum_value_3 = np.minimum(residual, target_distance_2)
    negative_penalty_5 = -(np.maximum(minimum_value_3, 0))
    return negative_penalty_5
