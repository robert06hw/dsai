def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 20.0
    product_3 = target_distance_2 * target_distance_2
    negative_penalty_4 = -product_3
    scores = np.where(residual >= 0, negative_penalty_4, 1000.0)
    return scores
