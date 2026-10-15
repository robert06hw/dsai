import numpy as np

def score(item, bins):
    residual = bins - item
    negative_penalty_2 = -(25.0)
    full_like_value_3 = np.full_like(residual, negative_penalty_2)
    maximum_value_4 = np.maximum(full_like_value_3, residual)
    minimum_value_5 = np.minimum(residual, maximum_value_4)
    negative_penalty_6 = -(minimum_value_5)
    return negative_penalty_6
