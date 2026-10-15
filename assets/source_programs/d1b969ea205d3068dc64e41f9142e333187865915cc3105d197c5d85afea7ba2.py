import numpy as np

def score(item, bins):
    residual = bins - item
    adjustment = residual + 1.0
    normalized_penalty = item / adjustment
    target_distance = residual - normalized_penalty
    product = target_distance * target_distance
    negative_penalty = -product
    return negative_penalty
