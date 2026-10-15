import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 25.0
    product_3 = residual * target_distance_2
    negative_penalty_4 = -(product_3)
    product_5 = negative_penalty_4 * product_3
    return product_5
