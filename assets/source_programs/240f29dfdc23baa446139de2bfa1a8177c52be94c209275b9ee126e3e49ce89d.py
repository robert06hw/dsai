import numpy as np

def score(item, bins):
    residual = bins - item
    score = np.where(residual < 0, 0, residual)
    score = np.where(score < 28.0, score, 0)
    score = np.where(score < 28.0, (score - 28.0) * (score - 28.0), 0)
    return score
