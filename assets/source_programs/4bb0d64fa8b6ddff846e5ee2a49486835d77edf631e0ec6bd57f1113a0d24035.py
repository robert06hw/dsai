import numpy as np

def score(item, bins):
    residual = bins - item
    residual_squared = residual ** 2
    target_distance_squared = (residual - 25.0) ** 2
    product = residual_squared * target_distance_squared
    penalty = -product
    return penalty
