import numpy as np

def score(item, bins):
    residual = bins - item
    maximum_value_2 = np.maximum(residual, 0)
    power_value_3 = np.power(maximum_value_2, 3)
    negative_penalty_4 = -power_value_3
    return negative_penalty_4
