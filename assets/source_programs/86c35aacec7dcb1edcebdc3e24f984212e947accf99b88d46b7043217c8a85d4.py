import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 12.0
    product_3 = target_distance_2 * target_distance_2
    return -(product_3)
