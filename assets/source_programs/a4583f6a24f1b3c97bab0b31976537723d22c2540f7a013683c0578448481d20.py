import numpy as np

def score(item, bins):
    residual = bins - item
    penalty = residual / (bins + 1.0)
    return -penalty
