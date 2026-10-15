import numpy as np

def score(item, bins):
    residual = bins - item
    target_distance_3 = residual - (0.25 * item)
    return -(target_distance_3 * target_distance_3)
