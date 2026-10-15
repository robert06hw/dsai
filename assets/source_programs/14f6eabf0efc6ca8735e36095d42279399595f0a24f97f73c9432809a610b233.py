def score(item, bins):
    residual = (bins - item)
    square_value_2 = np.square(residual)
    negative_penalty_3 = -(square_value_2)
    score_array = np.maximum(negative_penalty_3, 0)
    max_score = np.max(score_array)
    return np.where(score_array == max_score, score_array, 0)
