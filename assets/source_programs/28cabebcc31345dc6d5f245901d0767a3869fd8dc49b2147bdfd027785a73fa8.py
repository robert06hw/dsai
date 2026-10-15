import numpy as np

def score(item, bins):
    residual = (bins - item)
    maximum_value_2 = np.maximum(residual, 0)
    adjustment_3 = (residual + 1e-10)
    maximum_value_4 = np.maximum(adjustment_3, 0)
    log_value_5 = np.log(maximum_value_4)
    product_6 = (maximum_value_2 * log_value_5)
    negative_penalty_7 = -(product_6)
    adjustment_8 = (negative_penalty_7 + 25.0)
    maximum_value_9 = np.maximum(adjustment_8, 0)
    return maximum_value_9
