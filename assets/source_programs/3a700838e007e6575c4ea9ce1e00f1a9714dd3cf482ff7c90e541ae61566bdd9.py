import numpy as np

def score(item, bins):
    residual = (bins - item)
    minimum_value_2 = np.minimum(residual, residual)
    negative_penalty_3 = -(minimum_value_2)
    negative_penalty_4 = -(25.0)
    full_like_value_5 = np.full_like(residual, negative_penalty_4)
    maximum_value_6 = np.maximum(negative_penalty_3, full_like_value_5)
    return maximum_value_6
