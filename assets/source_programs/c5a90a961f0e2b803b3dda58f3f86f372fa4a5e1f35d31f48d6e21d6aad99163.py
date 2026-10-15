def score(item, bins):
    feasible_mask = bins >= item
    residual = bins - item
    product = residual * feasible_mask
    squared_product = product * product
    score = np.where(feasible_mask, squared_product, 0)
    return score
