import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = np.maximum(residual, 0)
    negative_penalty_3 = -np.square(adjustment_2)
    return negative_penalty_3
