import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment = residual / bins
    negative_penalty = -adjustment
    return negative_penalty
