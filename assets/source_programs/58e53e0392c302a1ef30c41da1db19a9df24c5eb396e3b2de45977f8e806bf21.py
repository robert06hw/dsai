import numpy as np

def score(item, bins):
    residual = bins - item
    score = np.where(residual > 0, np.full_like(residual, -25.0), residual)
    return score
