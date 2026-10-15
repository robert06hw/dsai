import numpy as np

def score(item, bins):
    residual = (bins - item)
    target_distance_2 = np.maximum(0, residual - 25.0)
    minimum_value_3 = np.minimum(residual, target_distance_2)
    negative_penalty_5 = -(minimum_value_3)
    return negative_penalty_5
