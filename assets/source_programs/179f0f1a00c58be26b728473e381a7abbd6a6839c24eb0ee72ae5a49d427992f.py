import numpy as np

def score(item, bins):
    residual = bins - item
    square_value = np.square(residual)
    negative_penalty = -square_value
    return negative_penalty
