import numpy as np

def score(item, bins):
    feasible_mask_1 = bins >= item
    residual = np.where(feasible_mask_1, bins - item, 0.0)
    score_values = -np.square(residual)
    return score_values
