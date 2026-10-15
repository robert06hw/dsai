import numpy as np

def score(item, bins):
    residual = (bins - item)
    square_value_2 = np.square(residual)
    square_value_3 = np.square(square_value_2)
    target_distance_4 = (square_value_3 - 25.0)
    sum_value_5 = np.sum(target_distance_4)
    negative_penalty_6 = -(sum_value_5)
    product_7 = (negative_penalty_6 * square_value_2)
    return product_7
