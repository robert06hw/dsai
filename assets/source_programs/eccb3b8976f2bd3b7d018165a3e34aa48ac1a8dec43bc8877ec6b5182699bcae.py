import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = np.maximum(residual - 5.0, 0)
    maximum_value_3 = target_distance_2 ** 2
    negative_penalty_5 = -maximum_value_3
    return negative_penalty_5
