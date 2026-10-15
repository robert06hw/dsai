import numpy as np

def score(item, bins):
    residual = (bins - item)
    adjusted_residual = np.maximum(residual, 0)
    score = -adjusted_residual ** 2
    return score
