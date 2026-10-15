import numpy as np

def score(item, bins):
    residual = bins - item
    return np.where(residual >= 0, residual, np.inf)
