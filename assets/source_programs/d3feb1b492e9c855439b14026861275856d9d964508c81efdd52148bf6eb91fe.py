import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = residual ** 2
    adjustment_3 = adjustment_2 ** 2
    target_distance_4 = adjustment_3 - 25.0
    product_5 = target_distance_4 * adjustment_2
    negative_penalty_6 = -product_5
    return negative_penalty_6
