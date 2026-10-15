def score(item, bins):
    feasible_mask = bins - item > 25.0
    where_value = np.where(feasible_mask, bins - item, 0)
    adjustment = where_value ** 3
    return -adjustment
