def score(item, bins):
    residual = bins - item
    minimum_value_2 = np.minimum(residual, 0)
    target_distance_3 = residual - 25.0
    maximum_value_4 = np.maximum(target_distance_3, 0)
    product_5 = minimum_value_2 * maximum_value_4
    product_6 = product_5 * residual
    product_7 = product_6 * maximum_value_4
    minimum_value_8 = np.minimum(product_7, 0)
    negative_penalty_9 = -minimum_value_8
    return negative_penalty_9
