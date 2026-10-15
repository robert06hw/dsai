import numpy as np

def score(item, bins):
    capacity = 100.0
    feasible_mask = bins - item > 0
    adjusted = (bins - item) ** 2
    where_value = np.where(feasible_mask, adjusted, 0)
    target_distance = where_value - 25.0
    where_value_2 = np.where(feasible_mask, target_distance, 0)
    sum_value = np.sum(where_value_2)
    negative_penalty = -(sum_value)
    product = negative_penalty * where_value
    return product
