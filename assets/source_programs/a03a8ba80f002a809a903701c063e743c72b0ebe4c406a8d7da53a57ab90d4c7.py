def score(item, bins):
    residual = bins - item
    feasible_mask_2 = residual >= 0.0
    product_3 = residual * feasible_mask_2
    product_4 = product_3 * product_3
    negative_penalty_5 = -product_4
    return negative_penalty_5
