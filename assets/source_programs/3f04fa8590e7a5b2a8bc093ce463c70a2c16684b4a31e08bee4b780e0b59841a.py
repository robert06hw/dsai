import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = residual - 15.0
    penalty_3 = distance_2 ** 2
    negative_penalty_4 = -penalty_3
    adjustment_5 = distance_2 + 1.0
    product_6 = negative_penalty_4 * adjustment_5
    argmax_value_7 = np.argmax(residual)
    adjustment_8 = product_6 + argmax_value_7
    return adjustment_8
