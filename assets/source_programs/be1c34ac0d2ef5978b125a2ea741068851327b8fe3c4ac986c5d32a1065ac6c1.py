def score(item, bins):
    residual = bins - item
    target_distance_2 = np.maximum(0, residual - 18.0)
    product_3 = np.square(target_distance_2)
    negative_penalty_4 = -product_3
    adjustment_5 = bins + 1.0
    normalized_penalty_6 = negative_penalty_4 / adjustment_5
    return normalized_penalty_6
