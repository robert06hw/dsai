def score(item, bins):
    feasible_mask_1 = bins - item > 0
    residual = np.where(feasible_mask_1, bins - item, 0.0)
    product_4 = residual * residual
    negative_penalty_5 = -product_4
    return negative_penalty_5
