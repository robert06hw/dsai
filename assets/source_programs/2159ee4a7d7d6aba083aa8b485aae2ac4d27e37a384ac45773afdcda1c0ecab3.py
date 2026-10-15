import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = residual - 40.0
    penalty = distance_2 * distance_2
    return np.maximum(0.0, -penalty)
