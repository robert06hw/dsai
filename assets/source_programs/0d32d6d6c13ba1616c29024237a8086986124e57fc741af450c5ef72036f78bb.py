import numpy as np

def score(item, bins):
    target_distance_1 = 100.0 - bins
    feasible_mask_2 = bins >= item
    product_3 = np.where(feasible_mask_2, target_distance_1, np.nan)
    return product_3
