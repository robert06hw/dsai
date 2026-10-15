import numpy as np

def score(item, bins):
    residual = bins - item
    distance_to_12 = np.abs(residual - 12.0)
    squared_distance = distance_to_12 ** 2
    penalty = -squared_distance
    return penalty
