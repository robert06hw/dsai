import numpy as np

def score(item, bins):
    residual = bins - item
    negative_penalty_4 = -(residual * residual)
    return negative_penalty_4
