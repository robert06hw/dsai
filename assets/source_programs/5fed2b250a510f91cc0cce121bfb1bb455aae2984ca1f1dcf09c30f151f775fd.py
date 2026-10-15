def score(item, bins):
    residual = bins - item
    mask = residual >= 0
    scores = np.where(mask, residual - 5.0, np.full_like(residual, -np.inf))
    return scores
