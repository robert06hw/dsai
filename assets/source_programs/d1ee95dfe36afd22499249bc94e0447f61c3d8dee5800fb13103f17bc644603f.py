import numpy as np

def score(item, bins):
    residual = bins - item
    square_value_2 = np.square(residual)
    negative_penalty_3 = -(square_value_2)
    return negative_penalty_3
