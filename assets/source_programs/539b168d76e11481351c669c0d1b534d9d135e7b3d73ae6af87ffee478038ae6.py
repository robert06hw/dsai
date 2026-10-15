import numpy as np

def score(item, bins):
    residual = bins - item
    squared_residual = residual * residual
    negative_penalty = -squared_residual
    return negative_penalty
