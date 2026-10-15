import numpy as np

def score(item, bins):
    residual = bins - item
    squared_residual = residual ** 2
    penalty = np.where(squared_residual >= 144, squared_residual - 144, 0)
    return penalty
