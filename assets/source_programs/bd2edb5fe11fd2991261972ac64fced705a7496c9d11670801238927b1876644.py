def score(item, bins):
    residual = bins - item
    negative_penalty = np.where(residual > 0, -(25.0), -(np.minimum(residual, 0)))
    return negative_penalty
