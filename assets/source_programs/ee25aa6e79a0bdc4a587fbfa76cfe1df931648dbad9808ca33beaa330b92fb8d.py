import numpy as np

def score(item, bins):
    residual = bins - item
    normalized_penalty = item / (residual + 1.0)
    adjusted_residual = residual - normalized_penalty
    product = adjusted_residual * adjusted_residual
    negative_penalty = -product
    return negative_penalty
