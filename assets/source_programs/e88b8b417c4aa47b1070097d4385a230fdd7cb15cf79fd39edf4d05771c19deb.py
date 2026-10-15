def score(item, bins):
    residual = (bins - item)
    maximum_value_2 = np.maximum(residual, 0)
    log_value_4 = np.log(maximum_value_2 + 1e-10)
    negative_penalty_6 = -(maximum_value_2 * log_value_4)
    maximum_value_8 = np.maximum(negative_penalty_6 + 25.0, 0)
    return maximum_value_8
