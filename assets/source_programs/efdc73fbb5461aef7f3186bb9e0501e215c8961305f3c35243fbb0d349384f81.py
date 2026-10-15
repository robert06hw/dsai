def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 15.0
    product_3 = target_distance_2 ** 2
    negative_penalty_4 = -product_3
    adjustment_5 = bins + 1.0
    product_6 = negative_penalty_4 * adjustment_5
    return product_6
