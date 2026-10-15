import numpy as np

def score(item, bins):
    residual = bins - item
    negative_penalty_2 = np.maximum(0, residual)
    return negative_penalty_2
