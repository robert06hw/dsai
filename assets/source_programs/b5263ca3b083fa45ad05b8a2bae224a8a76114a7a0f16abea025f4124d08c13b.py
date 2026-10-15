def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 5.0
    maximum_value_3 = np.maximum(target_distance_2, 0)
    product_4 = maximum_value_3 * maximum_value_3
    negative_penalty_5 = -product_4
    return negative_penalty_5
