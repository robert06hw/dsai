def score(item, bins):
    residual = bins - item
    negative_penalty_2 = np.where(residual >= 0, residual, -residual)
    return negative_penalty_2
