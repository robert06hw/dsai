import numpy as np

def score(item, bins):
    feasible_mask = bins >= item
    target_distance = bins - item
    where_value = np.where(feasible_mask, target_distance, 0.0)
    score = where_value * where_value
    return -score
