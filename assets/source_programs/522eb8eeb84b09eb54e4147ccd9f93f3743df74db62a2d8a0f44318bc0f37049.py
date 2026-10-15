def score(item, bins):
    residual = bins - item
    max_2 = np.maximum(residual, 0)
    max_3 = np.maximum(max_2 - 25.0, 0)
    product_5 = residual * max_3
    product_6 = product_5 * product_5
    penalty = -product_6
    return penalty
