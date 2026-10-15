def score(item, bins):
    residual = bins - item
    distance_2 = residual - 15.0
    product_3 = distance_2 * distance_2
    negative_penalty_4 = -product_3
    adjustment_5 = bins + 1.0
    product_6 = negative_penalty_4 * adjustment_5
    return product_6
