import numpy as np

def score(item, bins):
    residual = bins - item
    normalized_penalty = item / (residual + 1.0)
    target_distance = residual - normalized_penalty
    product = target_distance * target_distance
    negative_penalty = -product
    return negative_penalty
