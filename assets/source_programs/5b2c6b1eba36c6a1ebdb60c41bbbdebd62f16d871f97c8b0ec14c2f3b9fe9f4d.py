import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = np.where(feasible_mask_1, bins - item, 0.0)
    product_4 = residual * residual
    negative_penalty_5 = -product_4
    score_arr = np.where(feasible_mask_1, -product_4, 0.0)
    return score_arr
