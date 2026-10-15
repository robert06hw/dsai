def score(item, bins):
    residual = bins - item
    residual_square = np.square(residual)
    bins_square = np.square(bins)
    bins_square_sub_residual_square = bins_square - residual_square
    bins_square_sub_residual_square_4 = np.square(bins_square_sub_residual_square)
    target_distance_4 = bins_square_sub_residual_square_4 - 25.0
    multiply_value_5 = np.multiply(target_distance_4, residual_square)
    negative_penalty_6 = -(multiply_value_5)
    return negative_penalty_6
