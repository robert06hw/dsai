import numpy as np

def score(item, bins):
    residual = (bins - item)
    max_value = np.maximum(residual, 0)
    adjusted_value = max_value ** 3
    penalty = -(adjusted_value)
    return penalty
