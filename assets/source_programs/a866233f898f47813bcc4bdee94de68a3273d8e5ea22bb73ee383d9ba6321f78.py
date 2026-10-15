import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = np.maximum(residual - 12.0, 0)  # Avoid negative values
    penalty = -distance_2**2
    return penalty
