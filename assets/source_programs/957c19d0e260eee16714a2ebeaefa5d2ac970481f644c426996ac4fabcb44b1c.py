import numpy as np

def score(item, bins):
    bins_remaining = bins - item
    feasible_mask = bins_remaining >= 5.0
    scores = np.where(feasible_mask, bins_remaining * bins_remaining, 0)
    return scores
