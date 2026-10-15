import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment_2 = residual ** 2
    negative_penalty_3 = -adjustment_2
    return negative_penalty_3
