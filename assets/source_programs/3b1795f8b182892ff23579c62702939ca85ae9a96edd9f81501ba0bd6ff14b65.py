import numpy as np

def score(item, bins):
    residual = bins - item
    normalized_penalty = residual ** 2 / (item + 1.0)
    negative_penalty = -normalized_penalty
    score = 0.3 * residual + negative_penalty
    return score
