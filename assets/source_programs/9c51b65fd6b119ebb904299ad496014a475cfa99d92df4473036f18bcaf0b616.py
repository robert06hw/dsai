import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 10.0
    maximum_value_3 = np.maximum(target_distance_2, 0.0)
    product_4 = residual * maximum_value_3
    product_5 = product_4 * product_4
    maximum_value_6 = np.maximum(product_5, 0.0)
    negative_penalty_7 = -(maximum_value_6)
    return negative_penalty_7
