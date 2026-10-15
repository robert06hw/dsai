import numpy as np

def score(item, bins):
    residual = bins - item
    distance_to_12 = np.abs(residual - 12.0)
    distance_squared = distance_to_12 * distance_to_12
    score = -distance_squared
    return score
