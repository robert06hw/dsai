import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 5.0
    maximum_value_3 = np.maximum(target_distance_2, 0)
    negative_penalty_4 = -(maximum_value_3)
    product_5 = negative_penalty_4 * maximum_value_3
    return product_5
