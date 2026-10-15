import numpy as np

def score(item, bins):
    # Calculate the score for each bin
    scores = ((bins - item) - 40.0) * ((bins - item) - 40.0)
    
    # Find the index of the highest score
    highest_score_index = np.argmax(scores)
    
    # Return a numpy array with zeros, except for the highest score index
    return np.zeros_like(bins) + (highest_score_index == np.arange(bins.size))
