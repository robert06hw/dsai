import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 28.0
    negative_penalty_4 = -np.square(target_distance_2)
    return negative_penalty_4
