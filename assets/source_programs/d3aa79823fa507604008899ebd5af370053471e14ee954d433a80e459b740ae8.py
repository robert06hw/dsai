import numpy as np

def score(item, bins):
    residual = bins - item
    score = np.where(residual > 25.0, residual, 0)
    score = np.where(residual > 25.0, score, residual - 25.0)
    score = np.where(residual > 25.0, score, 0)
    score = score**3
    score = -score
    return score
