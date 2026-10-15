import numpy as np

def score(item, bins):
    residual = bins - item
    adjusted_2 = residual ** 2
    negative_penalty_3 = -adjusted_2
    return negative_penalty_3
