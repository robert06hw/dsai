def score(item, bins):
    residual = bins - item
    maximum_value_2 = np.maximum(residual, 0)
    adjustment_3 = maximum_value_2 ** 2
    negative_penalty_4 = -adjustment_3
    return negative_penalty_4
