import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = residual ** 2
    target_distance_3 = adjustment_2 - 25.0
    product_4 = adjustment_2 * target_distance_3
    negative_penalty_5 = -product_4
    normalized_penalty_6 = negative_penalty_5 / bins
    return normalized_penalty_6
