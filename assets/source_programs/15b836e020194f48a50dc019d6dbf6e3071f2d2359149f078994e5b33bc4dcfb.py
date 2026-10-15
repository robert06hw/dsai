def score(item, bins):
    residual = (bins - item)
    negative_penalty_2 = -(residual)
    return negative_penalty_2
