import numpy as np

def score(item, bins):
    residual = (bins - item)
    target_distance_2 = (residual - 25.0)
    adjustment_3 = (target_distance_2 ** 3)
    negative_penalty_4 = -(adjustment_3)
    return negative_penalty_4
