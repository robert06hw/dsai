import numpy as np

def score(item, bins):
    feasible_mask_1 = (100.0 - bins) * (bins >= item) > np.max((100.0 - bins) * (bins >= item))
    feasible_mask_2 = bins >= item
    feasible_mask = feasible_mask_1 & feasible_mask_2
    return np.where(feasible_mask, 1, 0)
