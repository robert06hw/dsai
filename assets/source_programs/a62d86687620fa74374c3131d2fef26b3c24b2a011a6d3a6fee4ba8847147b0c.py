import numpy as np

def score(item, bins):
    feasible_mask = bins >= item
    score_values = np.where(feasible_mask, bins - item, 0)
    return -score_values ** 3
