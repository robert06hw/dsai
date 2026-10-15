import numpy as np

def score(item, bins):
    residual = (bins - item)
    target_distance_2 = np.maximum(0, residual - 28.0)
    negative_penalty_4 = -np.power(target_distance_2, 2)
    return negative_penalty_4
