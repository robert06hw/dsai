import numpy as np

def score(item, bins):
    feasible_mask = bins - item > 0
    residual = np.clip(bins - item, 0, np.inf)
    score = -residual**2
    return score
