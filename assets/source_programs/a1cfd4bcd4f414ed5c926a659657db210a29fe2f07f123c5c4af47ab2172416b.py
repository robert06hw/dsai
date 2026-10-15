import numpy as np

def score(item, bins):
    residual = bins - item
    scores = residual[np.where(residual >= 0)]
    return scores
