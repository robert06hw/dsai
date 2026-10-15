import numpy as np

def score(item, bins):
    residual = (bins - item)
    maximum_value_2 = np.maximum(0, residual)
    product_3 = (maximum_value_2 * maximum_value_2)
    negative_penalty_4 = -(product_3)
    return negative_penalty_4
