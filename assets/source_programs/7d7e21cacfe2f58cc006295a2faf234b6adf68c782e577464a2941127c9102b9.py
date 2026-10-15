def score(item, bins):
    residual = bins - item
    square_value_2 = np.square(residual)
    negative_penalty_3 = np.maximum(square_value_2, 0)
    return negative_penalty_3
