import numpy as np

def score(item, bins):
    residual = bins - item
    product_2 = 0.75 * item
    target_distance_3 = residual - product_2
    product_4 = target_distance_3 ** 2
    negative_penalty_5 = -product_4
    return negative_penalty_5
