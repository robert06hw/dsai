import numpy as np

def score(item, bins):
    # Calculate the scoring function for each bin
    scores = (-(((bins - item) * (bins - item)) / (bins + 1.0))) + (0.45 * (bins - item))
    
    # Find the index of the bin with the highest score
    max_index = np.argmax(scores)
    
    # Return a new array with all scores set to 0, except the highest score index
    return np.where(np.arange(bins.shape[0]) == max_index, scores, 0.0)
