def score(item, bins):
    residual = bins - item
    negative_penalty_3 = -(residual ** 2)
    return negative_penalty_3
