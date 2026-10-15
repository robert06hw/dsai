import numpy as np

def score(item, bins):
    residual = bins - item
    maximum_value_2 = np.maximum(residual, 0)
    adjustment_3 = residual + 1e-10
    log_value_4 = np.log(adjustment_3)
    product_5 = maximum_value_2 * log_value_4
    negative_penalty_6 = -product_5
    adjustment_7 = negative_penalty_6 + 25.0
    return np.maximum(adjustment_7, 0)
