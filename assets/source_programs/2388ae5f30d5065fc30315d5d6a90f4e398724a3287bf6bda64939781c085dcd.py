import numpy as np

def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = np.maximum(bins - item, 0.0)
    product_4 = residual * residual
    negative_penalty_5 = -product_4
    max_score_idx = np.argmax(negative_penalty_5)
    return negative_penalty_5 - negative_penalty_5[max_score_idx]
