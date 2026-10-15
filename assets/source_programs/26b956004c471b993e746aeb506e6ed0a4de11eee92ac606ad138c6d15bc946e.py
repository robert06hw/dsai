import numpy as np

def score(item, bins):
    residual = bins - item
    distance_2 = residual - 5.0
    product_3 = distance_2 * distance_2
    negative_penalty_4 = -product_3
    return negative_penalty_4
