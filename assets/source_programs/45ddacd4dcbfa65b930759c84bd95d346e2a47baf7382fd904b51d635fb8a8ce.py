import numpy as np

def score(item, bins):
    residual = bins - item
    feasible_mask = residual >= 0.0
    product = residual * feasible_mask
    product_squared = product * product
    negative_penalty = -product_squared
    return negative_penalty
