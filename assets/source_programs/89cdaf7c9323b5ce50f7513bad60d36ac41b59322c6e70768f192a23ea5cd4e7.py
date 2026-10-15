def score(item, bins):
    residual = bins - item
    product_2 = residual * residual
    negative_penalty_3 = -product_2
    return negative_penalty_3
