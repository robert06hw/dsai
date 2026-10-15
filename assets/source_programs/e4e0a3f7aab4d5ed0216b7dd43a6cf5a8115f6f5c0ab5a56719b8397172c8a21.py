def score(item, bins):
    residual = bins - item
    score = np.maximum(residual - 5.0, 0) * -(residual - 5.0)
    return score
