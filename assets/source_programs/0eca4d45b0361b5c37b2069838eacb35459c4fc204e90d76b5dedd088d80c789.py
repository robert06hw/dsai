import numpy as np

def score(item, bins):
    residual = bins - item
    squared_residual = residual ** 2
    score = -squared_residual
    return score
