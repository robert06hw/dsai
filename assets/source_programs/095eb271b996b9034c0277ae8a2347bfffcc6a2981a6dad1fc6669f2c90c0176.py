import numpy as np

def score(item, bins):
    residual = bins - item
    feasible_mask = residual >= 0.0
    score = np.where(feasible_mask, residual * residual, np.inf)
    return score
