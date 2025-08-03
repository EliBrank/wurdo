from english_words import get_english_words_set

def build_word_deletion_map(word_list):
    """
    Builds a dictionary mapping words to a list of other words
    that can be created by removing a single letter.
    
    Args:
        word_list (set): A set of all valid words.
    
    Returns:
        dict: A dictionary where keys are words and values are a list of
              valid words that can be formed by removing one letter.
    """
    word_deletion_map = {}
    
    # Iterate through each word in the valid word list
    for original_word in word_list:
        valid_deletions = []
        
        # Generate all possible words by removing one letter
        for i in range(len(original_word)):
            # Create a new word by skipping the letter at index i
            deleted_word = original_word[:i] + original_word[i+1:]
            
            # Check if the new word is also in the valid word list
            if deleted_word in word_list:
                valid_deletions.append(deleted_word)
        
        # If any valid deletions were found, add them to our map
        if valid_deletions:
            word_deletion_map[original_word] = valid_deletions
            
    return word_deletion_map
