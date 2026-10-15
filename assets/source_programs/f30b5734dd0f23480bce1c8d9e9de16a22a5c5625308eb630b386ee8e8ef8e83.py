import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = residual - 15.0
    square_3 = distance_2 ** 2
    adjustment_4 = distance_2 + 1.0
    square_5 = square_3 * adjustment_4
    penalty_6 = -square_5
    max_value_7 = np.argmax(residual)
    adjustment_8 = penalty_6 + max_value_7
    return adjustment_8
