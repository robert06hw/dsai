import numpy as np

def score(item, bins):
    residual = bins - item
    negative_penalty_2 = -(25.0)
    maximum_value_3 = np.maximum(negative_penalty_2, residual)
    minimum_value_4 = np.minimum(residual, maximum_value_3)
    negative_penalty_5 = -(minimum_value_4)
    return negative_penalty_5
