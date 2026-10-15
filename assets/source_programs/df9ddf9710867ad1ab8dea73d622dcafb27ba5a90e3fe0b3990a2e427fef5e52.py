import numpy as np

def score(item, bins):
    residual = bins - item
    squared_residual = np.square(residual)
    penalty = -squared_residual
    return penalty
