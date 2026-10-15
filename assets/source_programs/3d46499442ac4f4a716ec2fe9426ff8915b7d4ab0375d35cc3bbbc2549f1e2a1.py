import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 12.0
    maximum_value_3 = np.maximum(0, target_distance_2)
    product_4 = maximum_value_3 * maximum_value_3
    negative_penalty_5 = -product_4
    maximum_value_6 = np.maximum(0, negative_penalty_5)
    return maximum_value_6
