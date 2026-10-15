import numpy as np

def score(item, bins):
    residual = bins - item
    square_value_2 = np.square(residual)
    target_distance_3 = np.square(residual) - 25.0
    product_4 = square_value_2 * target_distance_3
    negative_penalty_5 = -product_4
    normalized_penalty_6 = negative_penalty_5 / bins
    return normalized_penalty_6
