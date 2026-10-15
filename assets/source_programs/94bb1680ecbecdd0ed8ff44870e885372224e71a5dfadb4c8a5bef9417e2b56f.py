def score(item, bins):
    residual = bins - item
    score = np.maximum(0, residual) ** 2
    return score
