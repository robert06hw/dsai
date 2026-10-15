import numpy as np

def score(item, bins):
    # Initialize the scores array with zeros
    scores = np.zeros_like(bins)
    
    # Calculate the scores using numpy vector operations
    scores = -(bins - item)**2
    
    return scores
