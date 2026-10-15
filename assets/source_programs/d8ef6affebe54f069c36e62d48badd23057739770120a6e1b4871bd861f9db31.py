import numpy as np

def score(item, bins):
    residual = bins - item
    adjusted_bins = residual + 1.0
    normalized_penalty = item / adjusted_bins
    target_distance = residual - normalized_penalty
    squared_distance = target_distance * target_distance
    negative_penalty = -squared_distance
    return negative_penalty
