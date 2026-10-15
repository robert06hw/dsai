def score(item, bins):
    feasible_mask = bins >= item
    residual = np.maximum(bins - item, 0.0)
    square_value = np.square(residual)
    negative_penalty = -square_value
    return negative_penalty
