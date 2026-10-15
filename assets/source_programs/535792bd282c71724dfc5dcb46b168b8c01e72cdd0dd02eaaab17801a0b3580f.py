import numpy as np

def score(item, bins):
    residual = (bins - item)
    target_distance_2 = (residual - 15.0)
    product_3 = (target_distance_2 * target_distance_2)
    negative_penalty_4 = -(product_3)
    adjustment_5 = (target_distance_2 + 1.0)
    product_6 = (negative_penalty_4 * adjustment_5)
    argmax_value_7 = np.argmax(residual)
    adjustment_8 = (product_6 + argmax_value_7)
    return adjustment_8
