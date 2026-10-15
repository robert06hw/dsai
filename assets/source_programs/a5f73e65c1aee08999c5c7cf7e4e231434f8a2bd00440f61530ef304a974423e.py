import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_2 = residual - 18.0
    product_3 = target_distance_2 * target_distance_2
    normalized_penalty_6 = product_3 / (bins + 1.0)
    return normalized_penalty_6
