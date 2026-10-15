import numpy as np

def score(item, bins):
    residual = bins - item
    square_value_2 = np.square(residual)
    negative_penalty_3 = -square_value_2
    adjustment_4 = negative_penalty_3 + 25.0
    return adjustment_4
