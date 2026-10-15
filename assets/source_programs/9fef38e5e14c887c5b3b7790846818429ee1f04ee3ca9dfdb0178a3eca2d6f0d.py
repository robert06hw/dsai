def score(item, bins):
    feasible_mask = bins >= item
    residual = np.where(feasible_mask, bins - item, 0.0)
    penalty = residual ** 2
    return -penalty
