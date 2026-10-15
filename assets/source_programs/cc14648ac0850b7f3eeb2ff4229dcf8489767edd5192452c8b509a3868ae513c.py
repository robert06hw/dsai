def score(item, bins):
    residual = bins - item
    negative_penalty_2 = -(25.0)
    maximum_value_3 = np.maximum(residual, negative_penalty_2)
    negative_penalty_5 = -(maximum_value_3)
    return negative_penalty_5
