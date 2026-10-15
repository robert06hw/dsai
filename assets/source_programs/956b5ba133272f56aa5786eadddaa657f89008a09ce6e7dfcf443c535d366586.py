def score(item, bins):
    residual = bins - item
    target_distance_2 = np.clip(residual - 5.0, 0.0, 100.0)
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = np.clip(product_3, -10000.0, 0.0)
    return negative_penalty_4
