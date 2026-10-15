import numpy as np

def score(item, bins):
    residual = bins - item
    mask = residual >= 5.0
    maximum_value = np.where(mask, residual - 5.0, 0)
    product = maximum_value * maximum_value
    negative_penalty = -product
    return negative_penalty
