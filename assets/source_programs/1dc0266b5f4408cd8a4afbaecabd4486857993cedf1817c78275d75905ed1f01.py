import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 5.0
    maximum_value_3 = np.maximum(target_distance_2, 0)
    product_5 = maximum_value_3 * target_distance_2
    return product_5
