import numpy as np

def score(item, bins):
    square_value_1 = np.square(bins)
    residual = (bins - item)
    square_value_3 = np.square(residual)
    target_distance_4 = (square_value_1 - square_value_3)
    square_value_5 = np.square(target_distance_4)
    target_distance_6 = (square_value_5 - 25.0)
    multiply_value_7 = np.multiply(target_distance_6, square_value_3)
    negative_penalty_8 = -(multiply_value_7)
    return negative_penalty_8
