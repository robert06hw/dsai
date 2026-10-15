import numpy as np

def score(item, bins):
    feasible_mask_1 = bins >= item
    residual = np.maximum(0, bins - item)
    product_4 = residual * residual
    negative_penalty_5 = -product_4
    return negative_penalty_5
