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


# --- Main Execution ---

# 1. Get a valid list of English words
# We'll use the 'web2' word list for this example.
print("Loading word list...")
word_set = get_english_words_set(['web2'], lower=True)
print(f"Loaded {len(word_set)} words.")

# Optional: Filter the list to a specific length range if needed for your game
# filtered_word_set = {word for word in word_set if 3 <= len(word) <= 7}
# print(f"Filtered to {len(filtered_word_set)} words of length 3-7.")

# 2. Build the deletion map
print("Building word deletion map...")
deletion_map = build_word_deletion_map(word_set)
print("Map built.")

# 3. Test the function
print("\n--- Testing the word deletion map ---")

test_words = ["start", "stare", "scorn", "cat", "hello", "python"]

for word in test_words:
    if word in deletion_map:
        print(f"Words that can be made by removing a letter from '{word}': {deletion_map[word]}")
    else:
        print(f"No valid words can be made by removing a letter from '{word}'.")
