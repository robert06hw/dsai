def score(item, bins):
    residual = bins - item
    negative_penalty_5 = np.where(residual >= 0, 0, -(residual + 25))
    return negative_penalty_5
