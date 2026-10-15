import numpy as np

def score(item, bins):
    residual = bins - item
    log_value = np.log(1 + residual)
    adjustment = np.maximum(log_value, 0)
    return adjustment
