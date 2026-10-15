import numpy as np

def score(item, bins):
    residual = bins - item
    residual_squared = residual ** 2
    target_distance_2 = (residual_squared - 25.0)
    product_3 = residual_squared * target_distance_2
    negative_penalty_5 = -product_3
    return negative_penalty_5
