def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 25.0
    minimum_value_3 = np.minimum(residual, target_distance_2)
    minimum_value_4 = np.minimum(minimum_value_3, 0)
    negative_penalty_6 = -(np.minimum(minimum_value_4, 0))
    return negative_penalty_6
