import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = np.square(residual)
    negative_penalty_3 = np.negative(adjustment_2)
    return negative_penalty_3
