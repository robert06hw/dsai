import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = 1.25 * item
    target_distance_3 = residual - product_2
    product_4 = np.multiply(target_distance_3, target_distance_3)
    negative_penalty_5 = np.negative(product_4)
    return negative_penalty_5
