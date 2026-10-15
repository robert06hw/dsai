import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = np.square(residual - 15.0)
    penalty = -np.square(distance_2)
    adjustment = bins + 1.0
    score = penalty * adjustment
    return score
