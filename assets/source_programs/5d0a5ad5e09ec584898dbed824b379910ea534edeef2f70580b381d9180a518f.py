def score(item, bins):
    bins_left = bins - item
    feasible_mask = bins_left > 0
    residual = np.maximum(bins_left, 0)
    product = residual * residual
    negative_penalty = -product
    score = np.where(feasible_mask, negative_penalty, 0.0)
    return score
