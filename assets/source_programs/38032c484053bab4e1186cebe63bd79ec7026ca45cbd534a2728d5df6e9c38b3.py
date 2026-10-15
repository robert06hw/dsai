import numpy as np

def score(item, bins):
    residual = bins - item
    penalty_1 = (residual * residual) / (item + 1.0)
    return -penalty_1
