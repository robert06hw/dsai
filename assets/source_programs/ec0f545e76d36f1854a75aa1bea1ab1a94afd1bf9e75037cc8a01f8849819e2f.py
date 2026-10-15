def score(item, bins):
    residual = (bins - item)
    maximum_value_2 = np.maximum(0, residual)
    product_3 = np.multiply(maximum_value_2, maximum_value_2)
    negative_penalty_4 = np.multiply(product_3, -1)
    return negative_penalty_4
